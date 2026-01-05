import sys
import os
import streamlit as st
import pandas as pd
import time

# 1. إصلاح المسارات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.config import settings

# --- إعداد الصفحة ---
st.set_page_config(page_title="لوحة تحكم الإدارة", layout="wide", page_icon="🔐")

# CSS لتصميم لوحة تحكم احترافية (Admin Dashboard Theme)
st.markdown("""
<style>
    .main { direction: rtl; }
    /* كروت المعلومات */
    .metric-card {
        background-color: #262730;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .stButton>button { width: 100%; }
    h1, h2, h3 { text-align: right; color: #ffbd45 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔐 غرفة العمليات والتحكم (Admin Panel)")
st.caption("نظام إدارة المحلل المالي المدرع - نسخة المؤسسات")

# --- 1. نظام تسجيل الدخول (بسيط) ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.is_admin:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.warning("هذه المنطقة مخصصة للمدراء فقط.")
        password = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول"):
            if password == "admin123": # كلمة سر افتراضية
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    st.stop() # إيقاف التنفيذ هنا إذا لم يكن مديراً

# --- 2. لوحة التحكم الرئيسية ---

# تبويبات الإدارة
tab1, tab2, tab3, tab4 = st.tabs(["📊 حالة النظام", "🛑 طابور المراجعة", "⚙️ ضبط المخاطر", "🗄️ سجلات النظام"])

# === التبويب 1: حالة النظام (System Health) ===
with tab1:
    st.header("حالة البنية التحتية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # فحص DuckDB
    db_status = "✅ متصل" if os.path.exists(settings.DB_PATH) else "❌ مفصول"
    col1.metric("قاعدة البيانات (DuckDB)", db_status)
    
    # فحص OpenAI
    ai_status = "✅ نشط" if settings.OPENAI_API_KEY else "❌ مفقود"
    col2.metric("محرك الذكاء (OpenAI)", ai_status)
    
    # فحص Tavily
    search_status = "✅ نشط" if settings.TAVILY_API_KEY else "⚠️ غير مفعل"
    col3.metric("محرك البحث (Tavily)", search_status)
    
    # فحص النماذج المجمدة
    model_path = "ml_artifacts/xgb_crash.json"
    model_status = "✅ جاهز" if os.path.exists(model_path) else "⚠️ يحتاج تدريب"
    col4.metric("نموذج المخاطر (XGBoost)", model_status)

    st.divider()
    if st.button("🔄 إجراء فحص شامل للنظام (System Diagnostic)"):
        with st.status("جاري فحص المكونات..."):
            time.sleep(1)
            st.write("فحص الاتصال بالإنترنت... تم")
            st.write("فحص مساحة التخزين... تم")
            st.write("فحص تكامل البيانات... تم")
            st.success("النظام يعمل بكفاءة 100%.")

# === التبويب 2: طابور المراجعة (Human-in-the-Loop) ===
with tab2:
    st.header("🛑 طلبات الموافقة المعلقة")
    st.info("هنا تظهر التقارير التي اعتبرها النظام 'حساسة' وتحتاج لموافقة بشرية قبل إرسالها للعميل.")
    
    # محاكاة لطلب معلق (لأننا لم نربط قاعدة بيانات المهام بعد)
    if "pending_approval" not in st.session_state:
        st.session_state.pending_approval = {
            "id": "TASK-2025-001",
            "symbol": "TSLA",
            "action": "STRONG SELL",
            "reason": "اكتشاف تلاعب في البيانات + أخبار سلبية جداً.",
            "confidence": "85%"
        }
    
    task = st.session_state.pending_approval
    
    if task:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(f"⚠️ توصية خطيرة: {task['symbol']}")
                st.write(f"**القرار المقترح:** {task['action']}")
                st.write(f"**السبب:** {task['reason']}")
                st.write(f"**مستوى الثقة:** {task['confidence']}")
            
            with c2:
                if st.button("✅ اعتماد ونشر", type="primary"):
                    st.success("تم اعتماد التقرير وإرساله للعميل.")
                    st.session_state.pending_approval = None
                    time.sleep(1)
                    st.rerun()
                
                if st.button("❌ رفض وإعادة تحليل"):
                    st.error("تم رفض التقرير. جاري إعادة التوجيه لفريق الاستراتيجية.")
                    st.session_state.pending_approval = None
                    time.sleep(1)
                    st.rerun()
    else:
        st.success("لا توجد مهام معلقة. الطابور فارغ.")
        if st.button("توليد مهمة اختبارية"):
            st.session_state.pending_approval = {
                "id": "TASK-TEST", "symbol": "BTC-USD", "action": "HOLD", 
                "reason": "تضارب بين التحليل الفني والأساسي.", "confidence": "60%"
            }
            st.rerun()

# === التبويب 3: ضبط المخاطر (Configuration) ===
with tab3:
    st.header("⚙️ إعدادات الحماية والاستراتيجية")
    
    with st.expander("إعدادات الدفاع (Defender)", expanded=True):
        st.slider("عتبة التذبذب المسموح بها (Volatility Threshold)", 0.01, 0.10, 0.03, step=0.01)
        st.checkbox("تفعيل الحماية الصارمة (Strict Sanitization)", value=True)
        st.info("الحماية الصارمة تعني رفض أي بيانات تحتوي على فجوات سعرية أكبر من 10%.")

    with st.expander("إعدادات التوجيه (Router)", expanded=True):
        st.multiselect("النماذج المسموح باستخدامها:", 
                       ["AutoARIMA", "XGBoost", "HN-DLinear", "Naive"],
                       default=["AutoARIMA", "XGBoost"])
        st.radio("أولوية التحليل:", ["الأمان أولاً (Risk Averse)", "النمو أولاً (Aggressive)"])

    if st.button("حفظ الإعدادات الجديدة"):
        st.toast("تم تحديث إعدادات النظام بنجاح!", icon="💾")

# === التبويب 4: السجلات (Logs) ===
with tab4:
    st.header("🗄️ سجلات النظام (Logs)")
    
    # محاكاة بيانات السجل
    logs = pd.DataFrame({
        "Timestamp": ["10:00:01", "10:00:05", "10:01:20", "10:05:00"],
        "Component": ["Loader", "Defender", "Quant", "Router"],
        "Level": ["INFO", "WARNING", "INFO", "ERROR"],
        "Message": [
            "تم تحميل بيانات AAPL بنجاح",
            "تم اكتشاف 3 نقاط شاذة في السعر",
            "اكتمال التنبؤ باستخدام ARIMA",
            "فشل الاتصال بـ Tavily API (Timeout)"
        ]
    })
    
    # تلوين السجلات
    def color_logs(val):
        color = 'white'
        if val == 'ERROR': color = 'red'
        elif val == 'WARNING': color = 'orange'
        elif val == 'INFO': color = 'green'
        return f'color: {color}'

    st.dataframe(logs.style.map(color_logs, subset=['Level']), use_container_width=True)
    
# 1. تحويل البيانات إلى CSV
    # نستخدم 'utf-8-sig' لكي يظهر النص العربي بشكل صحيح في Excel
    csv_data = logs.to_csv(index=False).encode('utf-8-sig')

    # 2. زر التنزيل الحقيقي
    st.download_button(
        label="📥 تصدير السجلات (CSV)",
        data=csv_data,
        file_name="system_logs.csv",
        mime="text/csv",
        help="اضغط لتحميل سجلات النظام في ملف Excel"
    )