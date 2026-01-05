import pandas as pd
import numpy as np

class VolatilityGuard:
    def __init__(self, window=14, threshold=0.03):
        """
        window: الفترة الزمنية لحساب التذبذب (14 يوم)
        threshold: الحد المسموح به للتذبذب (3%)
        """
        self.window = window
        self.threshold = threshold

    def check_volatility(self, df: pd.DataFrame) -> dict:
        """
        يفحص استقرار السعر.
        Returns:
            dict: {is_volatile (bool), current_volatility (float), message (str)}
        """
        if df.empty or len(df) < self.window:
            return {
                "is_volatile": False, 
                "score": 0.0, 
                "message": "بيانات غير كافية لفحص التذبذب"
            }

        try:
            # 1. حساب العائد اليومي (Daily Returns)
            # pct_change يحسب نسبة التغير بين اليوم والأمس
            df['returns'] = df['close'].pct_change()

            # 2. حساب الانحراف المعياري للعائد (Rolling Standard Deviation)
            # هذا هو المقياس العالمي للتذبذب (Volatility)
            current_volatility = df['returns'].tail(self.window).std()
            
            # التعامل مع القيم الفارغة (NaN)
            if pd.isna(current_volatility):
                current_volatility = 0.0

            # 3. الحكم (Decision)
            is_volatile = current_volatility > self.threshold
            
            status = "خطر (High Risk)" if is_volatile else "آمن (Stable)"
            score_percentage = current_volatility * 100

            message = f"مستوى التذبذب الحالي: {score_percentage:.2f}% - الحالة: {status}"
            
            if is_volatile:
                print(f"⚠️ تحذير: تم رصد تذبذب عالي ({score_percentage:.2f}%)")

            return {
                "is_volatile": is_volatile,
                "score": current_volatility,
                "message": message
            }

        except Exception as e:
            return {
                "is_volatile": False, 
                "score": 0.0, 
                "message": f"خطأ في حساب التذبذب: {e}"
            }