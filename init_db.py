from app.core.database import get_db_connection

print("⏳ جاري تهيئة قاعدة البيانات...")

# هذا السطر السحري سيقوم بإنشاء الملف والجداول فوراً
conn = get_db_connection()

print("✅ تم إنشاء ملف data/finance.duckdb بنجاح!")