from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.engine.state import FinancialState
from tavily import TavilyClient
import os
# 🟢 استيراد العقل الاستراتيجي (المفقود سابقاً)
from app.engine.strategy_team.chief_commander import chief_node  # المدير
from app.engine.strategy_team.critic import critic_node # الناقد

from app.engine.execution_team.workers.data_loader import DataLoader
from app.engine.execution_team.workers.quant_analyst import quant_analyst_node
from app.engine.execution_team.workers.sentiment_analyst import sentiment_node
from app.engine.execution_team.workers.reporter import reporter_node
from app.engine.execution_team.workers.fundamental import fundamental_analyst_node
from app.engine.execution_team.workers.defender import defender_node

# إعدادات النماذج
chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
# تأكد من وجود المفتاح في .env أو تعامل مع الخطأ بمرونة
try:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
except:
    tavily = None

# ==========================================
# 1. عقدة الدردشة الذكية (للمتابعة والنقاش)
# ==========================================
def conversational_node(state):
    print("--- 💬 Chat: التحدث مع المستخدم ---")
    
    messages = state.get('messages', [])
    last_user_msg = messages[-1].content
    
    # استرجاع سياق التحليل السابق
    symbol = state.get('symbol')
    report = state.get('final_report')
    fund_summary = state.get('fundamental_summary', '') # 🟢 إضافة البيانات الأساسية للسياق

    # بناء السياق للموديل
    context_block = ""
    if symbol and report:
        context_block = f"""
        --- بيانات التحليل السابق للسهم {symbol} ---
        التقرير النهائي:
        {report}
        
        بيانات القوائم المالية:
        {fund_summary}
        -------------------------------------------
        """

    # البحث الحي (اختياري) لدعم الإجابة
    tavily_context = ""
    if tavily:
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
    2. إذا كان السؤال عن السهم المحلل ({symbol})، استخدم البيانات المالية والتقرير الموجود في السياق لدعم إجابتك.
    3. إذا كان السؤال عاماً أو عن شركة أخرى، اعتمد على معلوماتك العامة والبحث الحي، وتجاهل سياق السهم السابق.
    """
    
    final_messages = [SystemMessage(content=system_prompt)] + messages
    response = chat_model.invoke(final_messages)
    
    return {"messages": [response]}

# ==========================================
# 2. تغليف عامل التحميل (Loader Node)
# ==========================================
def loader_wrapper(state):
    symbol = state['symbol']
    print(f"--- 📥 Loader: جاري تحميل بيانات {symbol} ---")
    
    loader = DataLoader()
    # نحاول جلب بيانات سنة كاملة
    success, msg = loader.fetch_and_store_data(symbol, period="1y")
    
    df = loader.get_data(symbol)
    
    if not success or df.empty:
        return {
            "market_data": None, 
            "final_report": f"❌ عذراً، لم أتمكن من العثور على بيانات للسهم {symbol}. تأكد من صحة الرمز.",
            "symbol": None
        }
    
    return {"market_data": df}

# ==========================================
# 3. بناء المخطط (The Assembly Line)
# ==========================================
# ==========================================
# 4. المخطط الجديد (The New Workflow)
# ==========================================
def create_workflow():
    workflow = StateGraph(FinancialState)
    
    # أ) إضافة العقد (المحطات)
    workflow.add_node("chief", chief_node)       # 🟢 جديد
    workflow.add_node("critic", critic_node)     # 🟢 جديد
    workflow.add_node("loader", loader_wrapper)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("fundamental", fundamental_analyst_node)
    workflow.add_node("quant", quant_analyst_node)
    workflow.add_node("reporter", reporter_node)
    
    # ب) رسم المسار
    workflow.set_entry_point("chief") # البداية عند المدير
    
    workflow.add_edge("chief", "loader")
    workflow.add_edge("loader", "fundamental")
    workflow.add_edge("fundamental", "sentiment")
    workflow.add_edge("sentiment", "quant")
    workflow.add_edge("quant", "reporter")
    
    workflow.add_edge("reporter", "critic") # التقرير يذهب للناقد
    
    # ج) المنطق الشرطي للناقد
    def router_after_critic(state):
        # ⚠️ ملاحظة: تأكد أن state.py يحتوي على is_quality_passed
        if state.get("is_quality_passed", False):
            return "end"
        return "rewrite"

    workflow.add_conditional_edges(
        "critic",
        router_after_critic,
        {
            "end": END,
            "rewrite": "reporter"
        }
    )
    
    return workflow.compile()