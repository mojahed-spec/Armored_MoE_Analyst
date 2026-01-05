import os
from dotenv import load_dotenv
from pathlib import Path

# 1. تحديد مسار ملف .env بدقة
# (نعود خطوتين للخلف من هذا الملف للوصول للمجلد الرئيسي)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"

# 2. تحميل الملف
load_dotenv(dotenv_path=env_path)

class Settings:
    # معلومات المشروع
    PROJECT_NAME: str = "Armored MoE Analyst (Dual Brain)"
    VERSION: str = "2.0.0"
    
    # المفاتيح الحساسة (يقرأها من البيئة)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    
    # مسارات البيانات
    DB_PATH: str = os.getenv("DB_PATH", "data/finance.duckdb")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "data/vector_store")
    
    # إعدادات النماذج
    MODEL_NAME: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.0

# إنشاء نسخة واحدة للاستخدام في كامل المشروع
settings = Settings()

# --- فحص الأمان (Sanity Check) ---
# لن يقلع النظام إذا كانت المفاتيح ناقصة
if not settings.OPENAI_API_KEY:
    raise ValueError("❌ خطأ قاتل: مفتاح OPENAI_API_KEY غير موجود في ملف .env")

if not settings.TAVILY_API_KEY:
    print("⚠️ تحذير: مفتاح TAVILY_API_KEY غير موجود. البحث في الويب لن يعمل.")