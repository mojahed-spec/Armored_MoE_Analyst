import pandas as pd
import numpy as np
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, Naive, SeasonalNaive

class TimeSeriesForecaster:
    def __init__(self):
        """
        تهيئة نماذج التنبؤ الإحصائية.
        نستخدم هذه النماذج لأنها سريعة جداً (C++) وتعمل بكفاءة على الأجهزة المحدودة.
        """
        self.models = [
            AutoARIMA(season_length=5), # النموذج الأذكى: يكتشف الأنماط تلقائياً
            Naive(),                    # النموذج البسيط: يتوقع استمرار السعر الحالي (للمقارنة)
            SeasonalNaive(season_length=5) # النموذج الموسمي: يتوقع تكرار نمط الأسبوع الماضي
        ]
        
    def predict_trend(self, df: pd.DataFrame, horizon: int = 7) -> dict:
        """
        يقوم بتحليل السلسلة الزمنية والتنبؤ بالمستقبل.
        
        Args:
            df: يجب أن يحتوي على الأعمدة ['date', 'close', 'symbol']
            horizon: عدد الأيام المراد التنبؤ بها (الافتراضي 7)
            
        Returns:
            dict: يحتوي على السعر المتوقع، نسبة التغير، وإشارة الترند.
        """
        # حماية من البيانات غير الكافية
        if df.empty or len(df) < 30:
            return {"status": "error", "message": "البيانات غير كافية للتحليل الزمني (أقل من 30 يوم)."}

        try:
            # 1. تجهيز البيانات لتناسب مكتبة StatsForecast
            # المكتبة تشترط أسماء أعمدة محددة: (ds: التاريخ, y: القيمة, unique_id: الرمز)
            input_df = df.rename(columns={'date': 'ds', 'close': 'y', 'symbol': 'unique_id'})
            input_df['ds'] = pd.to_datetime(input_df['ds'])
            
            # هام جداً: نحتفظ فقط بالأعمدة الأساسية ونتخلص من الحجم وغيره
            # لتجنب خطأ "Exogenous Variables" عند التنبؤ بالمستقبل
            input_df = input_df[['unique_id', 'ds', 'y']]

            # 2. تشغيل المحرك
            sf = StatsForecast(
                models=self.models,
                freq='D',   # التردد يومي
                n_jobs=-1   # استخدام كل أنوية المعالج للسرعة القصوى
            )
            
            # التدريب على البيانات التاريخية
            sf.fit(input_df)
            
            # التنبؤ بالمستقبل
            forecast_df = sf.predict(h=horizon)
            
            # 3. تحليل النتائج واستخلاص "الزبدة"
            last_actual_price = df['close'].iloc[-1]
            
            # نعتمد على AutoARIMA كنموذج رئيسي للدقة
            future_price = forecast_df['AutoARIMA'].iloc[-1]
            
            # حساب نسبة التغير المتوقعة
            change_pct = ((future_price - last_actual_price) / last_actual_price) * 100
            
            # تحديد إشارة الترند (بناءً على نسبة التغير)
            if change_pct > 1.0:
                trend = "BULLISH 📈 (صعود)"
            elif change_pct < -1.0:
                trend = "BEARISH 📉 (هبوط)"
            else:
                trend = "NEUTRAL ↔️ (اتجاه عرضي)"
            
            return {
                "status": "success",
                "current_price": last_actual_price,
                "forecast_price_7d": future_price,
                "change_pct": change_pct,
                "trend_signal": trend,
                # نعيد البيانات الخام لرسمها في الواجهة لاحقاً
                "raw_forecast": forecast_df 
            }

        except Exception as e:
            # التعامل مع أي خطأ رياضي دون إيقاف النظام
            return {"status": "error", "message": f"فشل التنبؤ الإحصائي: {str(e)}"}