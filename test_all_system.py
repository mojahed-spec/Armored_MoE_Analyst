import sys
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 1. إعداد البيئة
load_dotenv()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

print("🚀 بدء اختبار النظام الشامل (System Diagnostic Test)...\n")

# ==========================================
# المرحلة 1: فحص البنية التحتية (Infrastructure)
# ==========================================
print("--- [1/5] فحص البنية التحتية والملفات ---")

required_files = [
    ".env",
    "ml_artifacts/xgb_crash.json",
    "ml_artifacts/isolation_forest.pkl",
    "cache/semantic_net.json",
    "data/finance.duckdb"
]

missing_files = []
for f in required_files:
    if os.path.exists(f):
        print(f"✅ ملف موجود: {f}")
    else:
        print(f"❌ ملف مفقود: {f}")
        missing_files.append(f)

if missing_files:
    print("⚠️ توقف! النظام غير جاهز. يرجى تشغيل factory_setup.py أولاً.")
    exit()

# ==========================================
# المرحلة 2: اختبار الأدوات العلمية (Components)
# ==========================================
print("\n--- [2/5] اختبار المكونات العلمية (Unit Tests) ---")

# أ) اختبار الدفاع (Sanitizer)
try:
    from app.components.defense.sanitizer import DataSanitizer
    sanitizer = DataSanitizer()
    # بيانات وهمية مع شذوذ
    df_dummy = pd.DataFrame({'close': [100, 101, 102, 5000, 103, 102]})
    df_clean, report = sanitizer.check_and_clean(df_dummy)
    if df_clean.iloc[3]['close'] < 200:
        print("✅ Sanitizer: نجح في كشف وتنظيف الشذوذ (5000 -> قيمة منطقية).")
    else:
        print("❌ Sanitizer: فشل في التنظيف.")
except Exception as e:
    print(f"❌ خطأ في اختبار الدفاع: {e}")

# ب) اختبار المخاطر (Crash Classifier)
try:
    from app.components.risk.crash_clf import CrashClassifier
    risk_clf = CrashClassifier()
    # بيانات وهمية (يجب أن تكون كافية لحساب المؤشرات)
    df_risk = pd.DataFrame({'close': np.random.normal(100, 5, 50).cumsum()})
    risk_score = risk_clf.predict_risk(df_risk)
    print(f"✅ Risk Model: النموذج يعمل وأعطى احتمالية: {risk_score:.2%}")
except Exception as e:
    print(f"❌ خطأ في اختبار المخاطر: {e}")

# ج) اختبار التحليل الأساسي (Metrics)
try:
    from app.components.fundamental.metrics import FundamentalMetrics
    fund_tool = FundamentalMetrics()
    # نجرب على سهم معروف
    res = fund_tool.get_key_metrics("AAPL")
    if res.get('status') == 'success':
        print(f"✅ Fundamental: نجح في جلب بيانات AAPL (P/E: {res['valuation'].get('Trailing_PE')})")
    else:
        print(f"⚠️ Fundamental: فشل الاتصال (قد يكون بسبب النت): {res.get('message')}")
except Exception as e:
    print(f"❌ خطأ في اختبار الأساسي: {e}")

# ==========================================
# المرحلة 3: اختبار العقل الاستراتيجي (Strategy Brain)
# ==========================================
print("\n--- [3/5] اختبار العقل الاستراتيجي (Chief Commander) ---")

try:
    from app.engine.strategy_team.chief_commander import chief_commander_node
    # محاكاة حالة مبدئية
    state_mock = {"symbol": "TSLA", "user_request": "تحليل شامل"}
    result = chief_commander_node(state_mock)
    
    plan = result.get('plan')
    sector = result.get('sector')
    
    if plan and sector:
        print(f"✅ Commander: حدد القطاع ({sector}) ووضع خطة من {len(plan)} خطوات.")
    else:
        print("❌ Commander: فشل في التخطيط.")
except Exception as e:
    print(f"❌ خطأ في العقل الاستراتيجي: {e}")

# ==========================================
# المرحلة 4: اختبار العقل التنفيذي (Execution Team)
# ==========================================
print("\n--- [4/5] اختبار العقل التنفيذي (Workers) ---")

try:
    from app.engine.execution_team.workers.data_loader import DataLoader
    loader = DataLoader()
    success, msg = loader.fetch_and_store_data("AAPL", period="1mo") # شهر واحد للسرعة
    if success:
        print("✅ Loader: نجح في تحميل البيانات وتخزينها في DuckDB.")
    else:
        print(f"❌ Loader: فشل التحميل ({msg})")
except Exception as e:
    print(f"❌ خطأ في العمال: {e}")

# ==========================================
# المرحلة 5: اختبار التكامل الكامل (Full Workflow)
# ==========================================
print("\n--- [5/5] التشغيل التجريبي للنظام (Integration Test) ---")

try:
    from app.engine.workflow import create_workflow
    
    app = create_workflow()
    
    inputs = {
        "symbol": "AAPL",
        "user_request": "هل السهم جيد للاستثمار؟"
    }
    
    print("⏳ جاري تشغيل المحرك (قد يستغرق بضع ثوانٍ)...")
    final_state = app.invoke(inputs)
    
    report = final_state.get('final_report')
    if report and len(report) > 50:
        print("\n🎉 النتيجة النهائية: تم إصدار التقرير بنجاح!")
        print("="*40)
        print(report[:300] + "...") # طباعة أول 300 حرف
        print("="*40)
    else:
        print("❌ النظام عمل لكنه لم يخرج تقريراً (فارغ).")

except Exception as e:
    print(f"❌ فشل التشغيل الكامل: {e}")

print("\n🏁 انتهى الاختبار.")