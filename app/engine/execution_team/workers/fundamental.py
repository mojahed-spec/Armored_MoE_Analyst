from app.components.fundamental.metrics import FundamentalMetrics

# تهيئة الأداة (يتم تحميلها مرة واحدة لسرعة الأداء)
metrics_analyzer = FundamentalMetrics()

def fundamental_analyst_node(state):
    """
    عامل التحليل الأساسي (Fundamental Analyst Worker).
    المهمة: تقييم صحة الشركة المالية (وليس سعر السهم).
    """
    print("--- 💼 Fundamental Analyst: دراسة القوائم المالية ---")
    
    symbol = state.get('symbol')
    
    if not symbol:
        return {"fundamental_data": {"error": "لم يتم تحديد رمز السهم."}}

    # 1. استخدام الأداة لجلب البيانات
    result = metrics_analyzer.get_key_metrics(symbol)
    
    # 2. التحقق من النتيجة
    if result.get('status') == 'error':
        print(f"   >> فشل التحليل المالي: {result['message']}")
        return {
            "fundamental_data": None,
            "fundamental_summary": f"تعذر الحصول على بيانات مالية لـ {symbol}."
        }

    # 3. استخراج البيانات المهمة للتقرير
    valuation = result['valuation']
    health = result['health']
    score = result['fundamental_score']
    summary = result['analysis_summary']
    
    # صياغة ملخص سريع (للمدير)
    report_summary = f"""
    التحليل الأساسي (Fundamental):
    - التقييم (P/E): {valuation.get('Trailing_PE', 'N/A')}
    - الديون/الملكية: {health.get('Debt_to_Equity', 'N/A')}
    - تقييم النظام: {score}/3
    - الملاحظات: {summary}
    """
    
    print(f"   >> تقييم الشركة المالي: {score}/3")

    # 4. تحديث الحالة
    # نرسل البيانات الخام (للاستخدام المستقبلي) + الملخص النصي
    return {
        "fundamental_data": result,
        "fundamental_summary": report_summary
    }