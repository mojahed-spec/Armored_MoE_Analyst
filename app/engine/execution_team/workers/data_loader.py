import yfinance as yf
import pandas as pd
from app.core.database import get_db_connection

class DataLoader:
    def __init__(self):
        # نفتح اتصالاً مع قاعدة البيانات عند إنشاء العامل
        self.conn = get_db_connection()

    def fetch_and_store_data(self, symbol: str, period: str = "2y"):
        """
        يجلب البيانات من الإنترنت ويخزنها في المستودع المحلي.
        
        Args:
            symbol: رمز السهم (مثلاً AAPL)
            period: المدة الزمنية (2y = سنتين، 1y = سنة، 1mo = شهر)
        """
        clean_symbol = symbol.strip().upper()
        print(f"--- 📥 Loader: جاري الاتصال بالسوق لجلب بيانات {clean_symbol} ---")
        
        try:
            # 1. الاتصال بـ Yahoo Finance
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period)
            
            # محاولة ثانية إذا فشل الجلب (أحياناً يفشل الاتصال الأول)
            if df.empty:
                print("   >> ⚠️ محاولة ثانية بمدى زمني أقصر (1 سنة)...")
                df = ticker.history(period="1y")
            
            if df.empty:
                return False, f"فشل تحميل البيانات للرمز {clean_symbol}. تأكد من صحة الرمز."

            # 2. تنظيف وتنسيق البيانات
            # نحتاج تحويل المؤشر (التاريخ) إلى عمود عادي
            df.reset_index(inplace=True)
            
            # التأكد من صيغة التاريخ (بدون توقيت زمني)
            df['Date'] = df['Date'].dt.date
            
            # اختيار الأعمدة المطلوبة فقط وإعادة تسميتها لتطابق قاعدة البيانات
            # الجدول في DuckDB يتوقع: symbol, date, open, high, low, close, volume
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            df['symbol'] = clean_symbol # إضافة عمود الرمز
            
            # 3. التخزين في DuckDB
            # استراتيجية التحديث: نحذف البيانات القديمة لهذا السهم ونضع الجديدة (لضمان التحديث)
            self.conn.execute(f"DELETE FROM stock_prices WHERE symbol = '{clean_symbol}'")
            
            # خدعة DuckDB الرائعة: إدخال DataFrame مباشرة باستخدام SQL
            self.conn.register('temp_df', df)
            self.conn.execute("""
                INSERT INTO stock_prices 
                (symbol, date, open, high, low, close, volume)
                SELECT symbol, date, open, high, low, close, volume FROM temp_df
            """)
            self.conn.unregister('temp_df') # تنظيف الذاكرة المؤقتة
            
            msg = f"تم بنجاح تحميل وتخزين {len(df)} يوم تداول لـ {clean_symbol}."
            print(f"   ✅ {msg}")
            return True, msg

        except Exception as e:
            error_msg = f"خطأ فني في التحميل: {str(e)}"
            print(f"   ❌ {error_msg}")
            return False, error_msg

    def get_data(self, symbol: str) -> pd.DataFrame:
        """
        وظيفة القراءة: يستخدمها باقي العمال (Defender, Quant) 
        للحصول على البيانات من المستودع المحلي بسرعة فائقة.
        """
        clean_symbol = symbol.strip().upper()
        try:
            query = f"SELECT * FROM stock_prices WHERE symbol = '{clean_symbol}' ORDER BY date ASC"
            return self.conn.execute(query).df()
        except Exception as e:
            print(f"⚠️ خطأ في قراءة البيانات: {e}")
            return pd.DataFrame() # إرجاع جدول فارغ في حال الخطأ