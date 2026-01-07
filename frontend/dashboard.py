import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import tempfile  # 🟢 (1) مكتبة جديدة للتعامل مع الملفات المؤقتة
# ... (بعد الاستيرادات)

def load_css(file_name):
    """دالة لقراءة ملف CSS وتطبيقه"""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ... (بعد st.set_page_config)

# استدعاء ملف التنسيق
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
try:
    load_css(css_path)
except FileNotFoundError:
    st.warning("ملف التصميم style.css غير موجود، سيتم استخدام التصميم الافتراضي.")

# ... (باقي الكود)
# 1. إصلاح المسارات لرؤية مجلد app (ضروري جداً)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# استيراد المحرك
from app.engine.workflow import create_workflow, conversational_node

# --- إعداد الصفحة ---
st.set_page_config(page_title="المحلل المالي المؤسساتي", layout="wide", page_icon="🏦")

# CSS لتحسين المظهر (Dark Mode Financial Theme)
st.markdown("""
<style>
    .main { direction: rtl; }
    .stTextInput > div > div > input { text-align: right; }
    
    /* صندوق التقرير المميز */
    .report-box { 
        background-color: #1e1e1e; 
        color: #e0e0e0; 
        padding: 25px; 
        border-radius: 12px; 
        border-right: 5px solid #00c853; /* خط أخضر جمالي */
        margin-top: 15px; 
        margin-bottom: 15px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    
    /* تنسيق العناوين داخل التقرير */
    .report-box h3 { color: #00c853 !important; margin-top: 20px; }
    .report-box strong { color: #ffffff; }
</style>
""", unsafe_allow_html=True)

st.title("🏦 المحلل المالي المدرع (Enterprise Edition)")
# إضافة صندوق رفع الصور في الشريط الجانبي
with st.sidebar:
    st.header("📸 المحلل البصري")
    uploaded_file = st.file_uploader("ارفع صورة لصفقة أو شارت", type=['png', 'jpg', 'jpeg'])
st.caption("نظام هجين: تحليل أساسي + فني + مشاعر + حماية من المخاطر")

# --- 2. تهيئة الذاكرة (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="مرحباً بك. أنا جاهز للعمل. اطلب تحليل شركة (مثال: **أرامكو** أو **AAPL**) وسأقوم بتشغيل الفريق الكامل.")
    ]

# تخزين المحرك لتسريع الأداء
if "app" not in st.session_state:
    st.session_state.app = create_workflow()

# تخزين آخر سياق (لتغذية المحادثة اللاحقة)
if "last_context" not in st.session_state:
    st.session_state.last_context = {"symbol": None, "report": "لا يوجد تحليل سابق.", "data": None}

# --- 3. نموذج استخراج النية (Intent Extraction) ---
extractor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def detect_intent(user_text):
    """
    يحدد هل المستخدم يريد تحليل سهم جديد أم مجرد دردشة.
    """
    prompt = f"""
    المستخدم أرسل: "{user_text}"
    
    مهمتك:
    1. هل يطلب المستخدم تحليل سهم جديد؟ (مثال: "تحليل أرامكو", "TSLA", "سعر الذهب").
    2. إذا نعم، استخرج الرمز (Ticker) فقط (مثال: AAPL, 2222.SR, BTC-USD).
    3. إذا كان سؤالاً عاماً أو متابعة للنقاش السابق، أجب بـ "None".
    
    الإجابة كلمة واحدة فقط: الرمز أو None.
    """
    try:
        response = extractor_llm.invoke([SystemMessage(content=prompt)])
        result = response.content.strip().replace("'", "").replace('"', "").upper()
        if "NONE" in result:
            return False, None
        return True, result
    except:
        return False, None

# --- 4. عرض تاريخ المحادثة ---
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        # معالجة عرض التقرير داخل الصندوق الأسود
        if "تقرير استشاري" in msg.content or "التحليل الأساسي" in msg.content:
             st.markdown(f'<div class="report-box">{msg.content}</div>', unsafe_allow_html=True)
        else:
             st.write(msg.content)

# --- 5. معالجة المدخلات (Main Logic) ---
if prompt := st.chat_input("اكتب طلبك هنا..."):
    
    # أ) عرض وحفظ سؤال المستخدم
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.write(prompt)

    # ب) التفكير والرد
    with st.chat_message("assistant"):
        with st.spinner("جاري معالجة الطلب..."):
            final_response = ""
            image_path = None

            # 1. المخرجات الأولية: حفظ الصورة مؤقتاً (Input Handling)
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    image_path = tmp_file.name

            # 2. العمليات (Processing)
            # المسار الأول: إذا وجدت صورة (الأولوية للبصر Vision Priority)
            if image_path:
                st.info("👁️ جاري تحليل الصورة المرفقة واستخراج بيانات الصفقة...")
                try:
                    inputs = {
                        "messages": st.session_state.messages,
                        "screenshot_path": image_path,
                        "symbol": None,
                        "user_request": prompt
                    }
                    result = st.session_state.app.invoke(inputs)
                    final_response = result.get('final_report', 'تم التحليل.')
                    
                    # تحديث السياق وعرض الشارت إذا توفرت بيانات من الصورة
                    if result.get('market_data') is not None:
                        st.session_state.last_context = {
                            "symbol": result.get('symbol'),
                            "report": final_response,
                            "data": result['market_data']
                        }
                        # رسم الشارت (نفس كود الرسم الأصلي الخاص بك)
                        df = result['market_data']
                        st.subheader(f"📊 التحليل الفني للسهم المكتشف: {result.get('symbol')}")
                        fig = go.Figure(data=[go.Candlestick(
                            x=pd.to_datetime(df['date']), open=df['open'], 
                            high=df['high'], low=df['low'], close=df['close']
                        )])
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    final_response = f"⚠️ خطأ في المحلل البصري: {e}"

            # المسار الثاني: التحليل النصي أو الدردشة (Fallback Logic)
            else:
                is_new_analysis, symbol = detect_intent(prompt)

                if is_new_analysis:
                    st.info(f"⚙️ جاري تشغيل بروتوكول التحليل للسهم: **{symbol}**...")
                    try:
                        inputs = {"symbol": symbol, "user_request": "تحليل شامل", "messages": st.session_state.messages}
                        result = st.session_state.app.invoke(inputs)
                        
                        if result.get('market_data') is None:
                            final_response = f"❌ لم أتمكن من العثور على بيانات للسهم **{symbol}**."
                        else:
                            final_response = result.get('final_report', 'تم التحليل.')
                            st.session_state.last_context = {"symbol": symbol, "report": final_response, "data": result['market_data']}
                            
                            # رسم الشارت الأصلي
                            df = result['market_data']
                            fig = go.Figure(data=[go.Candlestick(
                                x=pd.to_datetime(df['date']), open=df['open'], 
                                high=df['high'], low=df['low'], close=df['close']
                            )])
                            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        final_response = f"⚠️ حدث خطأ تقني: {e}"

                else:
                    # مسار الدردشة العادية (Chat)
                    last_ctx = st.session_state.last_context
                    context_msg = f"سياق: {last_ctx['report']}\nسؤال: {prompt}"
                    chat_inputs = {
                        "messages": st.session_state.messages + [HumanMessage(content=context_msg)],
                        "symbol": last_ctx['symbol'],
                        "final_report": last_ctx['report']
                    }
                    resp_dict = conversational_node(chat_inputs)
                    final_response = resp_dict['messages'][-1].content

            # 3. المخرجات (Output Visualization)
            if "تقرير" in final_response or "التحليل" in final_response:
                st.markdown(f'<div class="report-box">{final_response}</div>', unsafe_allow_html=True)
            else:
                st.write(final_response)
            
            st.session_state.messages.append(AIMessage(content=final_response))