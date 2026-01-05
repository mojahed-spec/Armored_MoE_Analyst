import pandas as pd
import numpy as np
import os

# محاولة استيراد PyTorch (قد لا يكون مثبتاً)
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# --- تعريف هيكل النموذج (DLinear) ---
# هذا هو الهيكل الذكي الذي يفصل "الترند" عن "الموسمية"
class DLinear(nn.Module if TORCH_AVAILABLE else object):
    def __init__(self, seq_len, pred_len, channels):
        super(DLinear, self).__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        
        # طبقات التحلل (Decomposition)
        self.linear_trend = nn.Linear(seq_len, pred_len)
        self.linear_seasonal = nn.Linear(seq_len, pred_len)

    def forward(self, x):
        # x shape: [Batch, Seq_Len, Channels]
        trend_init = torch.mean(x, dim=1, keepdim=True).repeat(1, self.seq_len, 1)
        seasonal_init = x - trend_init
        
        # التنبؤ بكل جزء على حدة
        trend_output = self.linear_trend(trend_init.permute(0,2,1)).permute(0,2,1)
        seasonal_output = self.linear_seasonal(seasonal_init.permute(0,2,1)).permute(0,2,1)
        
        return trend_output + seasonal_output

# --- كلاس المشغل (The Handler) ---
class NeuralForecaster:
    def __init__(self, model_path="ml_artifacts/hn_dlinear.pth", seq_len=30, pred_len=7):
        """
        model_path: مسار النموذج المدرب (من Colab)
        seq_len: طول النافذة التي ينظر إليها النموذج للوراء (مثلاً 30 يوم)
        """
        self.model_path = model_path
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.model = None
        self.is_ready = False

        if TORCH_AVAILABLE and os.path.exists(model_path):
            try:
                # تحميل النموذج
                self.model = DLinear(seq_len, pred_len, channels=1)
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                self.model.eval() # وضع الاستنتاج
                self.is_ready = True
                print("✅ Neural: تم تفعيل الشبكة العصبية (DLinear).")
            except Exception as e:
                print(f"⚠️ Neural: خطأ في تحميل النموذج: {e}")
        else:
            status = "مكتبة torch غير موجودة" if not TORCH_AVAILABLE else "ملف النموذج غير موجود"
            print(f"ℹ️ Neural: النموذج العصبي غير نشط ({status}).")

    def predict(self, df: pd.DataFrame) -> dict:
        """
        التنبؤ باستخدام الشبكة العصبية.
        """
        # إذا لم يكن النموذج جاهزاً، نعتذر وننسحب
        if not self.is_ready:
            return {"status": "skipped", "message": "النموذج العصبي غير جاهز."}

        # التأكد من كفاية البيانات (نحتاج 30 يوم على الأقل للتدريب)
        if len(df) < self.seq_len:
            return {"status": "error", "message": f"نحتاج {self.seq_len} يوم على الأقل."}

        try:
            # 1. تجهيز البيانات (آخر 30 يوم)
            last_window = df['close'].tail(self.seq_len).values
            
            # تطبيع البيانات (Normalization) - مهم جداً للشبكات العصبية
            mean_val = np.mean(last_window)
            std_val = np.std(last_window) + 1e-5
            normalized_input = (last_window - mean_val) / std_val
            
            # تحويل لـ Tensor
            input_tensor = torch.tensor(normalized_input, dtype=torch.float32).unsqueeze(0).unsqueeze(2)
            
            # 2. التنبؤ
            with torch.no_grad():
                output_tensor = self.model(input_tensor)
            
            # 3. عكس التطبيع (Denormalization) للحصول على السعر الحقيقي
            normalized_pred = output_tensor.squeeze().numpy()
            real_pred = (normalized_pred * std_val) + mean_val
            
            # النتيجة النهائية (آخر يوم في التوقع)
            target_price = real_pred[-1]
            last_price = df['close'].iloc[-1]
            change_pct = ((target_price - last_price) / last_price) * 100
            
            return {
                "status": "success",
                "model": "HN-DLinear",
                "current_price": last_price,
                "forecast_price": target_price,
                "change_pct": change_pct,
                "raw_data": real_pred.tolist()
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}