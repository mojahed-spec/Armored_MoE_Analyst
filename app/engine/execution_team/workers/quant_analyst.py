from app.components.forecasting.statistical import TimeSeriesForecaster
from app.engine.execution_team.workers.data_loader import DataLoader 

# تهيئة أدوات التنبؤ مرة واحدة لسرعة الأداء
forecaster = TimeSeriesForecaster()
loader = DataLoader()

def quant_analyst_node(state):
    """
    عامل التحليل الكمي (Quant Analyst Worker).
    المهمة: تحليل السلاسل الزمنية، كشف الترند، والتنبؤ بالسعر المستقبلي.
    """
    print("--- 🔢 Quant Analyst: بدء النمذجة الرياضية ---")
    
    symbol = state.get('symbol')
    
    # 1. استلام البيانات (يفضل البيانات النظيفة القادمة من Defender)
    # إذا لم تكن موجودة، نطلبها من Loader كخطة طوارئ
    df = state.get('market_data')
    
    if df is None or df.empty:
        print("   >> تنبيه: البيانات غير متوفرة في الحالة، جاري طلبها من المصدر...")
        df = loader.get_data(symbol)
        
    if df.empty:
        return {
            "technical_report": "فشل التحليل الفني: لا توجد بيانات تاريخية كافية.",
            "forecast_summary": "لا توجد بيانات."
        }

    # 2. تشغيل محرك التنبؤ (Statistical Engine)
    # نتوقع للمستقبل القريب (7 أيام) لأن النماذج الإحصائية أدق في المدى القصير
    result = forecaster.predict_trend(df, horizon=7)
    
    # 3. معالجة النتائج وكتابة التقرير
    if result.get('status') == 'error':
        report = f"خطأ في النموذج الإحصائي: {result.get('message')}"
        forecast_summary = "تعذر التنبؤ."
    else:
        # استخراج الأرقام الرئيسية
        current_price = result['current_price']
        target_price = result['forecast_price_7d']
        change_pct = result['change_pct']
        trend_signal = result['trend_signal']
        
        # صياغة التقرير الفني بلغة الأرقام
        report = f"""
        التحليل الفني (Quantitative Forecast):
        - السعر الحالي: {current_price:.2f}
        - الاتجاه المتوقع: {trend_signal}
        - السعر المستهدف (7 أيام): {target_price:.2f}
        - نسبة التغير المتوقعة: {change_pct:.2f}%
        
        بناءً على نماذج السلاسل الزمنية (AutoARIMA)، يظهر السهم زخماً {'إيجابياً' if change_pct > 0 else 'سلبياً'} إحصائياً.
        """
        
        forecast_summary = f"{trend_signal} | هدف: {target_price:.2f}"
        print(f"   >> التنبؤ: {forecast_summary}")

    # 4. تحديث الحالة
    return {
        "technical_report": report,           # التقرير النصي الكامل
        "forecast_summary": forecast_summary, # ملخص سريع للموجه
        "forecast_data": result.get('raw_forecast') # البيانات الخام للرسم البياني
    }