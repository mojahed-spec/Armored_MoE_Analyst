import pandas as pd
import numpy as np
import joblib
import os

class DataSanitizer:
    def __init__(self, model_path="ml_artifacts/isolation_forest.pkl"):
        """
        يقوم بتحميل نموذج كشف الشذوذ (Isolation Forest) المدرب مسبقاً.
        """
        self.model = None
        self.is_ready = False
        
        # محاولة تحميل النموذج من الخزنة
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.is_ready = True
                print("✅ Sanitizer: تم تفعيل نظام الدفاع (Isolation Forest).")
            except Exception as e:
                print(f"❌ خطأ في تحميل نموذج الدفاع: {e}")
        else:
            print(f"⚠️ تحذير: ملف الدفاع غير موجود في {model_path}. سيتم تمرير البيانات دون فحص.")

    def check_and_clean(self, df: pd.DataFrame, col='close') -> tuple[pd.DataFrame, str]:
        """
        يفحص البيانات ويكتشف الهجمات أو الأخطاء (Anomalies) ويعالجها.
        
        Returns:
            - df_clean: البيانات بعد التنظيف
            - report: تقرير عما تم اكتشافه
        """
        # حماية من البيانات الفارغة
        if df is None or df.empty or len(df) < 10:
            return df, "البيانات غير كافية للفحص."

        # إذا لم يكن النموذج جاهزاً، نمرر البيانات كما هي (Fail Open)
        if not self.is_ready:
            return df, "نظام الدفاع غير نشط (تم تمرير البيانات)."

        try:
            # 1. تجهيز البيانات للفحص
            # Isolation Forest يحتاج مصفوفة 2D
            data_values = df[[col]].values

            # 2. الكشف (Detection)
            # النتيجة: 1 (طبيعي) ، -1 (شاذ/هجوم)
            # ملاحظة: في الإنتاج يفضل عمل fit على بيانات تاريخية و predict على الجديدة
            # هنا سنقوم بـ fit_predict للسرعة على البيانات الحالية
            anomalies = self.model.fit_predict(data_values)
            
            # حساب عدد النقاط المشبوهة
            num_anomalies = (anomalies == -1).sum()
            
            # إذا لم نجد شيئاً، نعيد البيانات كما هي
            if num_anomalies == 0:
                return df, "✅ البيانات سليمة (Clean)."

            # 3. المعالجة (Sanitization)
            # استراتيجية: الاستبدال بالاستيفاء الخطي (Linear Interpolation)
            # لا نحذف الصفوف لأن ذلك يكسر التسلسل الزمني
            
            df_clean = df.copy()
            
            # تحديد أماكن الشذوذ واستبدالها بـ NaN
            df_clean.loc[anomalies == -1, col] = np.nan
            
            # ملء الفراغات بمتوسط القيم المجاورة
            df_clean[col] = df_clean[col].interpolate(method='linear', limit_direction='both')
            
            report = f"🚨 تم اكتشاف {num_anomalies} نقاط شاذة وتم إصلاحها (Sanitized)."
            print(f"   >> {report}")
            
            return df_clean, report

        except Exception as e:
            error_msg = f"خطأ أثناء عملية التعقيم: {str(e)}"
            print(f"⚠️ {error_msg}")
            return df, error_msg