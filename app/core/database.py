import duckdb
from app.core.config import settings

# متغير عالمي لحفظ الاتصال (Singleton Pattern)
# الهدف: منع فتح ملف قاعدة البيانات عدة مرات مما يسبب تضارباً (File Lock)
_db_connection = None

def get_db_connection():
    """
    يعيد اتصالاً نشطاً بقاعدة البيانات. إذا لم يكن موجوداً، يقوم بإنشائه.
    """
    global _db_connection
    
    if _db_connection is None:
        try:
            # 1. فتح الاتصال (read_only=False يسمح بالكتابة والقراءة)
            _db_connection = duckdb.connect(settings.DB_PATH, read_only=False)
            
            print(f"✅ Database: تم الاتصال بنجاح بالمستودع {settings.DB_PATH}")
            
            # 2. التأكد من وجود الجدول الأساسي (هيكل البيانات)
            # حتى لو كان الملف جديداً، هذا يضمن أن الجدول جاهز لاستقبال البيانات
            _db_connection.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    symbol VARCHAR,
                    date DATE,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    volume BIGINT,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
        except Exception as e:
            print(f"❌ Database Error: فشل خطير في الاتصال بقاعدة البيانات: {e}")
            raise e # نوقف النظام لأن العمل بدون قاعدة بيانات مستحيل
            
    return _db_connection