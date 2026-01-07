import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient

# --- استيراد الحالة ---
from app.engine.state import FinancialState

# --- استيراد العقول (الاستراتيجية) ---
from app.engine.strategy_team.chief_commander import chief_node
from app.engine.strategy_team.critic import critic_node

# --- استيراد العمال (التنفيذ) ---
from app.engine.execution_team.workers.data_loader import DataLoader
from app.engine.execution_team.workers.vision_analyst import vision_node
from app.engine.execution_team.workers.defender import defender_node
from app.engine.execution_team.workers.fundamental import fundamental_analyst_node
from app.engine.execution_team.workers.sentiment_analyst import sentiment_node
from app.engine.execution_team.workers.quant_analyst import quant_analyst_node
from app.engine.execution_team.workers.reporter import reporter_node

# --- إعدادات النماذج والعملاء ---
chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

try:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
except:
    tavily = None

# ==========================================
# 1. عقدة الدردشة الذكية (Utility Function)
# ==========================================
def conversational_node(state):
    """
    دالة مستقلة لإدارة الدردشة مع الذاكرة والسياق.
    """
    print("--- 💬 Chat: التحدث مع المستخدم ---")
    
    messages = state.get('messages', [])
    last_user_msg = messages[-1].content if messages else ""
    
    # استرجاع سياق التحليل السابق
    symbol = state.get('symbol')
    report = state.get('final_report')
    fund_summary = state.get('fundamental_summary', '')

    # بناء السياق للموديل
    context_block = ""
    if symbol and report:
        context_block = f"""
        --- بيانات التحليل السابق للسهم {symbol} ---
        التقرير النهائي:
        {report}
        
        ملخص القوائم المالية:
        {fund_summary}
        -------------------------------------------
        """

    # البحث الحي (اختياري)
    tavily_context = ""
    if tavily and last_user_msg:
        try:
            search = tavily.search(query=last_user_msg, topic="news", max_results=2)
            tavily_context = "\n".join([r['content'] for r in search['results']])
        except:
            pass

    # هندسة الأمر (System Prompt)
    system_prompt = f"""
    أنت مستشار مالي ذكي ومحترف.
    
    {context_block}
    
    معلومات حية من البحث (إن وجدت):
    {tavily_context}
    
    التعليمات:
    1. أجب على سؤال المستخدم بدقة.
    2. إذا كان السؤال عن السهم المحلل ({symbol})، استخدم البيانات الموجودة في السياق.
    3. إذا كان السؤال عاماً، اعتمد على معلوماتك العامة.
    """
    
    # إرسال الطلب للنموذج
    response = chat_model.invoke([SystemMessage(content=system_prompt)] + messages)
    
    return {"messages": [response]}

# ==========================================
# 2. تغليف عامل التحميل (Loader Wrapper)
# ==========================================
def loader_wrapper(state):
    symbol = state.get('symbol')
    print(f"--- 📥 Loader: جاري تحميل بيانات {symbol} ---")
    
    if not symbol:
        return {"final_report": "❌ خطأ: لا يوجد رمز سهم للتحميل."}

    loader = DataLoader()
    success, msg = loader.fetch_and_store_data(symbol, period="1y")
    
    df = loader.get_data(symbol)
    
    if not success or df is None or df.empty:
        return {
            "market_data": None, 
            "final_report": f"❌ عذراً، لم أتمكن من العثور على بيانات للسهم {symbol}. تأكد من صحة الرمز.",
        }
    
    return {"market_data": df}

# ==========================================
# 3. بناء المخطط (Main Workflow)
# ==========================================
def create_workflow():
    workflow = StateGraph(FinancialState)
    
    # ---------------------------------------------------------
    # أ) إضافة العقد (Nodes)
    # ---------------------------------------------------------
    workflow.add_node("chief", chief_node)           # المدير
    workflow.add_node("vision", vision_node)         # المحلل البصري
    workflow.add_node("loader", loader_wrapper)      # التحميل
    workflow.add_node("defender", defender_node)     # 🛡️ المدافع (تم تفعيله)
    workflow.add_node("fundamental", fundamental_analyst_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("quant", quant_analyst_node)
    workflow.add_node("reporter", reporter_node)
    workflow.add_node("critic", critic_node)         # الناقد

    # ---------------------------------------------------------
    # ب) نقطة البداية والقرار الأول (Chief Logic)
    # ---------------------------------------------------------
    workflow.set_entry_point("chief")

    def route_start(state):
        # 1. إذا وجد المدير صورة، نذهب للمحلل البصري
        if state.get("screenshot_path"):
            return "vision"
        # 2. وإلا نذهب للتحميل المباشر
        return "loader"

    workflow.add_conditional_edges(
        "chief",
        route_start,
        {
            "vision": "vision",
            "loader": "loader"
        }
    )
    
    # ---------------------------------------------------------
    # ج) ربط المسار التسلسلي (The Pipeline)
    # ---------------------------------------------------------
    
    # 1. من الرؤية إلى التحميل (لإكمال البيانات الناقصة)
    workflow.add_edge("vision", "loader")
    
    # 2. من التحميل إلى الدفاع (Sanitization)
    workflow.add_edge("loader", "defender")
    
    # 3. من الدفاع إلى التحليل الأساسي
    workflow.add_edge("defender", "fundamental")
    
    # 4. بقية العمال بالتسلسل
    workflow.add_edge("fundamental", "sentiment")
    workflow.add_edge("sentiment", "quant")
    workflow.add_edge("quant", "reporter")
    
    # 5. التسليم للناقد
    workflow.add_edge("reporter", "critic")
    
    # ---------------------------------------------------------
    # د) حلقة الجودة (Critic Logic)
    # ---------------------------------------------------------
    def router_after_critic(state):
        # إذا وافق الناقد (أو تجاوزنا عدد المحاولات) ننهي
        if state.get("is_quality_passed", False):
            return "end"
        return "rewrite" # وإلا نعيد للصحفي

    workflow.add_conditional_edges(
        "critic",
        router_after_critic,
        {
            "end": END,
            "rewrite": "reporter"
        }
    )
    
    return workflow.compile()