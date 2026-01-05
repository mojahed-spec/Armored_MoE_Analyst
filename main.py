import os
from dotenv import load_dotenv
from app.engine.workflow import create_workflow

# تحميل المتغيرات البيئية
load_dotenv()

def main():
    print("==========================================")
    print("🤖 Armored MoE Analyst - النظام المالي المدرع")
    print("==========================================")
    
    # بناء الرسم البياني (The Brain)
    try:
        app = create_workflow()
    except ImportError:
        print("❌ خطأ: لم يتم العثور على ملف workflow.py أو هناك خطأ فيه.")
        return
    except Exception as e:
        print(f"❌ خطأ في بناء النظام: {e}")
        return

    while True:
        print("\n------------------------------------------")
        symbol = input("📈 أدخل رمز السهم (أو 'q' للخروج): ").strip().upper()
        
        if symbol.lower() == 'q':
            print("👋 وداعاً!")
            break
            
        if not symbol:
            continue
            
        user_req = input("💬 هل لديك سؤال محدد؟ (اتركه فارغاً لتحليل شامل): ").strip()
        if not user_req:
            user_req = "قم بعمل تحليل استثماري شامل لهذا السهم."

        print(f"\n⚙️  جاري استدعاء الفريق لتحليل {symbol}...")
        
        # إعداد المدخلات
        inputs = {
            "symbol": symbol,
            "user_request": user_req,
            "retry_count": 0
        }

        # تشغيل النظام
        try:
            # نستخدم invoke لتشغيل العملية كاملة وانتظار النتيجة
            final_state = app.invoke(inputs)
            
            report = final_state.get("final_report", "عذراً، لم يتم إنتاج تقرير نهائي.")
            
            print("\n📝 === التقرير النهائي ===")
            print(report)
            print("==========================\n")
            
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء التحليل: {e}")

if __name__ == "__main__":
    main()