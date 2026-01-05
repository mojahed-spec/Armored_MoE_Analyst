from app.components.defense.sanitizer import DataSanitizer
from app.components.defense.volatility import VolatilityGuard
from app.engine.execution_team.workers.data_loader import DataLoader

# تهيئة أدوات الدفاع مرة واحدة (للحفاظ على الموارد)
sanitizer = DataSanitizer()
volatility_guard = VolatilityGuard()
loader = DataLoader()

def defender_node(state):
    """
    عامل الدفاع (Defender Worker).
    المهمة: حماية النظام من البيانات المسمومة (Adversarial Attacks)
    والتحقق من استقرار السوق قبل السماح بالتحليل العميق.
    """
    print("--- 🛡️ Defender: تفعيل بروتوكولات الحماية ---")
    
    symbol = state.get('symbol')
    
    # 1. جلب البيانات الخام من المستودع
    # المدافع يستدعي Loader داخلياً ليحصل على أحدث نسخة
    df = loader.get_data(symbol)
    
    if df.empty:
        return {
            "risk_report": {"status": "error", "message": "لا توجد بيانات للفحص."},
            "market_data": None
        }

    # 2. خط الدفاع الأول: التعقيم (Sanitization)
    # كشف الهجمات العدائية أو الأخطاء في البيانات (مثل قفزات السعر الوهمية)
    df_clean, sanity_report = sanitizer.check_and_clean(df, col='close')
    
    # 3. خط الدفاع الثاني: فحص التذبذب (Volatility Check)
    # هل السوق آمن للتداول أم خطير جداً؟ (إذا التذبذب عالٍ، نحذر المدير)
    volatility_status = volatility_guard.check_volatility(df_clean)
    
    # 4. تجميع التقرير الأمني
    defense_summary = f"""
    تقرير الدفاع والأمان:
    - حالة البيانات: {sanity_report}
    - حالة السوق: {volatility_status['message']}
    - مستوى التذبذب: {volatility_status['score']*100:.2f}%
    """
    
    print(f"   >> الحالة الأمنية: {volatility_status['message']}")

    # 5. تحديث الحالة (State Update)
    # نمرر البيانات النظيفة فقط لباقي الفريق لضمان دقة التحليل
    return {
        "market_data": df_clean,      # البيانات المعتمدة (Clean Data)
        "risk_report": {              # تقرير للمدير
            "sanity": sanity_report,
            "volatility": volatility_status
        },
        "defense_report": defense_summary
    }