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
        """
        # تنظيف الرمز الأساسي
        clean_symbol = symbol.strip().upper()
        
        # 🟢 بداية التعديل: إصلاح الرموز الخاصة (Mapping Fix)
        # Yahoo Finance يستخدم رموزاً خاصة للذهب والعملات، نحولها هنا
        original_symbol = clean_symbol # نحتفظ بالاسم الأصلي للطباعة
        
        if clean_symbol == "XAUUSD" or clean_symbol == "GOLD":
            clean_symbol = "GC=F" # العقود الآجلة للذهب
            print(f"   >> 🔄 تم تحويل الرمز {original_symbol} إلى {clean_symbol} ليتوافق مع Yahoo Finance.")
        elif clean_symbol == "EURUSD":
            clean_symbol = "EURUSD=X"
        elif clean_symbol == "GBPUSD":
            clean_symbol = "GBPUSD=X"
        elif clean_symbol == "BTC":
            clean_symbol = "BTC-USD"
            
        print(f"--- 📥 Loader: جاري الاتصال بالسوق لجلب بيانات {clean_symbol} ---")
        
        try:
            # 1. الاتصال بـ Yahoo Finance
            ticker = yf.Ticker(clean_symbol)
            df = ticker.history(period=period)
            
            # محاولة ثانية إذا فشل الجلب
            if df.empty:
                print("   >> ⚠️ محاولة ثانية بمدى زمني أقصر (1 سنة)...")
                df = ticker.history(period="1y")
            
            if df.empty:
                return False, f"فشل تحميل البيانات للرمز {clean_symbol}. تأكد من صحة الرمز."

            # 2. تنظيف وتنسيق البيانات
            df.reset_index(inplace=True)
            df['Date'] = df['Date'].dt.date
            
            # تنسيق الأعمدة لقاعدة البيانات
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            # ⚠️ ملاحظة هامة: نخزن البيانات باسم الرمز الأصلي (مثل XAUUSD)
            # لكي يجده باقي الفريق (المحلل الفني والكمي) بنفس الاسم الذي يعرفونه
            df['symbol'] = original_symbol 
            
            # 3. التخزين في DuckDB
            # نحذف البيانات القديمة لنفس الرمز (الأصلي)
            self.conn.execute(f"DELETE FROM stock_prices WHERE symbol = '{original_symbol}'")
            
            self.conn.register('temp_df', df)
            self.conn.execute("""
                INSERT INTO stock_prices 
                (symbol, date, open, high, low, close, volume)
                SELECT symbol, date, open, high, low, close, volume FROM temp_df
            """)
            self.conn.unregister('temp_df')
            
            msg = f"تم بنجاح تحميل وتخزين {len(df)} يوم تداول لـ {original_symbol}."
            print(f"   ✅ {msg}")
            return True, msg

        except Exception as e:
            error_msg = f"خطأ فني في التحميل: {str(e)}"
            print(f"   ❌ {error_msg}")
            return False, error_msg

    def get_data(self, symbol: str) -> pd.DataFrame:
        """
        وظيفة القراءة: يستخدمها باقي العمال
        """
        clean_symbol = symbol.strip().upper()
        try:
            query = f"SELECT * FROM stock_prices WHERE symbol = '{clean_symbol}' ORDER BY date ASC"
            return self.conn.execute(query).df()
        except Exception as e:
            print(f"⚠️ خطأ في قراءة البيانات: {e}")
            return pd.DataFrame()