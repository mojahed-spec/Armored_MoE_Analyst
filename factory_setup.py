import os
import json
import joblib
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest

# التأكد من وجود المجلدات
os.makedirs("ml_artifacts", exist_ok=True)
os.makedirs("cache", exist_ok=True)

print("🚀 بدء تشغيل مصنع البيانات والنماذج...")

# ---------------------------------------------------------
# 1. بناء الشبكة الدلالية (للعقل الاستراتيجي)
# ---------------------------------------------------------
print("🧠 جاري بناء الشبكة الدلالية (Semantic Net)...")
semantic_net = {
    "SECTORS": {
        "TSLA": "EV_TECH",
        "AAPL": "CONSUMER_ELECTRONICS",
        "NVDA": "SEMICONDUCTORS",
        "2222.SR": "ENERGY_OIL",
        "ARAMCO": "ENERGY_OIL",
        "BTC-USD": "CRYPTOCURRENCY"
    },
    "RELATIONS": {
        "EV_TECH": ["Interest Rates", "Battery Cost", "AI Regulation"],
        "ENERGY_OIL": ["OPEC", "Geopolitics", "Global Demand"],
        "CRYPTOCURRENCY": ["SEC Regulation", "Tech Sentiment", "Inflation"]
    }
}
with open("cache/semantic_net.json", "w", encoding="utf-8") as f:
    json.dump(semantic_net, f, ensure_ascii=False, indent=4)
print("   ✅ تم حفظ: cache/semantic_net.json")

# ---------------------------------------------------------
# 2. بناء نموذج المخاطر (XGBoost Crash Predictor)
# ---------------------------------------------------------
print("📉 جاري تدريب نموذج كشف الانهيار (XGBoost)...")
# بيانات وهمية للتدريب الأولي
X = np.random.rand(100, 3) # [RSI, Volatility, Trend]
y = np.random.randint(0, 2, 100) # [0: Safe, 1: Crash]

xgb_model = xgb.XGBClassifier(n_estimators=10, max_depth=3)
xgb_model.fit(X, y)
xgb_model.save_model("ml_artifacts/xgb_crash.json")
print("   ✅ تم حفظ: ml_artifacts/xgb_crash.json")

# ---------------------------------------------------------
# 3. بناء نموذج الدفاع (Isolation Forest)
# ---------------------------------------------------------
print("🛡️ جاري تدريب نموذج الدفاع (Sanitizer)...")
# بيانات طبيعية
X_normal = np.random.normal(100, 10, (200, 1))
iso_model = IsolationForest(contamination=0.05)
iso_model.fit(X_normal)
joblib.dump(iso_model, "ml_artifacts/isolation_forest.pkl")
print("   ✅ تم حفظ: ml_artifacts/isolation_forest.pkl")

print("\n🎉 اكتمل التجهيز! النظام جاهز الآن لاستقبال كود المنطق.")