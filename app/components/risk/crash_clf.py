import xgboost as xgb
import pandas as pd
import numpy as np
import os

class CrashClassifier:
    def __init__(self, model_path="ml_artifacts/xgb_crash.json"):
        """
        يقوم بتحميل نموذج XGBoost المدرب مسبقاً.
        """
        self.model = xgb.XGBClassifier()
        self.is_ready = False
        
        # محاولة تحميل النموذج من المجلد
        if os.path.exists(model_path):
            try:
                self.model.load_model(model_path)
                self.is_ready = True
                print("✅ CrashClassifier: تم تحميل نموذج المخاطر (XGBoost) بنجاح.")
            except Exception as e:
                print(f"❌ خطأ في تحميل النموذج: {e}")
        else:
            print(f"⚠️ تنبيه: ملف النموذج غير موجود في {model_path}. سيعمل النظام بدون حماية مؤقتاً.")

    def predict_risk(self, df: pd.DataFrame) -> float:
        """
        يستقبل بيانات السهم التاريخية، يحسب المؤشرات، ويتنبأ بالخطر.
        Returns:
            probability (float): من 0.0 (آمن) إلى 1.0 (انهيار وشيك).
        """
        # إذا لم يكن النموذج جاهزاً أو البيانات قليلة، نفترض الأمان (0.0)
        if not self.is_ready or df.empty or len(df) < 15:
            return 0.0

        try:
            # 1. هندسة الخصائص (Feature Engineering) اللحظية
            # يجب أن نحسب نفس الخصائص التي تدرب عليها النموذج في المصنع:
            # [RSI, Volatility, Price_Change]
            
            # أ) تغيير السعر (Price Change)
            last_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            price_change = (last_price - prev_price) / prev_price
            
            # ب) التذبذب (Volatility) - انحراف معياري لآخر 5 أيام
            volatility = df['close'].pct_change().tail(5).std()
            
            # ج) مؤشر القوة النسبية (RSI) - معادلة يدوية سريعة
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # تنظيف القيم (NaN handling)
            volatility = 0.0 if np.isnan(volatility) else volatility
            rsi = 50.0 if np.isnan(rsi) else rsi # 50 هو خط المنتصف (محايد)
            price_change = 0.0 if np.isnan(price_change) else price_change

            # 2. تجهيز البيانات للنموذج
            # المصفوفة يجب أن تكون بنفس ترتيب التدريب: [RSI, Volatility, PriceChange]
            features = np.array([[rsi, volatility, price_change]])
            
            # 3. التنبؤ (Prediction)
            # نستخدم predict_proba للحصول على "احتمالية" وليس مجرد 0 أو 1
            # [0] تعني الصف الأول، [1] تعني احتمالية الكلاس 1 (الانهيار)
            crash_prob = self.model.predict_proba(features)[0][1]
            
            return float(crash_prob)

        except Exception as e:
            print(f"⚠️ خطأ أثناء حساب المخاطر: {e}")
            return 0.0 # نفشل بأمان (Fail Safe)