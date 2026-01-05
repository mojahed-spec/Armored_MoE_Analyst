from app.components.forecasting.statistical import TimeSeriesForecaster
from app.engine.execution_team.workers.data_loader import DataLoader 

# تهيئة أدوات التنبؤ مرة واحدة
forecaster = TimeSeriesForecaster()
loader = DataLoader()

def technical_analyst_node(state):
    """
    عامل التحليل الفني (Technical Analyst).
    المهمة: تحليل السلاسل الزمنية وتحديد اتجاه السعر المستقبلي (7 أيام).
    """
    print("--- 📉 Technical Analyst: بدء نمذجة السلاسل الزمنية ---")
    
    symbol = state.get('symbol')
    
    # 1. استلام البيانات (يفضل البيانات النظيفة من Defender)
    # إذا لم تتوفر، نطلبها من Loader كخطة بديلة
    df = state.get('market_data')
    
    if df is None or df.empty:
        print("   >> تنبيه: البيانات غير متوفرة في الحالة، جاري طلبها من المصدر...")
        df = loader.get_data(symbol)
        
    if df.empty:
        return {"technical_report": "فشل التحليل الفني: لا توجد بيانات تاريخية كافية."}

    # 2. تشغيل محرك التنبؤ (Statistical Engine)
    # نتوقع للمستقبل القريب (7 أيام)
    result = forecaster.predict_trend(df, horizon=7)
    
    # 3. معالجة النتائج وكتابة التقرير
    if result['status'] == 'error':
        report = f"خطأ في النموذج الإحصائي: {result['message']}"
        forecast_summary = "تعذر التنبؤ."
    else:
        # استخراج الأرقام الرئيسية
        current_price = result['current_price']
        target_price = result['forecast_price_7d']
        change_pct = result['change_pct']
        trend_signal = result['trend_signal']
        
        # صياغة التقرير الفني
        report = f"""
        التحليل الفني (Technical Forecast):
        - السعر الحالي: {current_price:.2f}
        - الاتجاه المتوقع: {trend_signal}
        - السعر المستهدف (7 أيام): {target_price:.2f}
        - نسبة التغير: {change_pct:.2f}%
        
        بناءً على نماذج (AutoARIMA)، السهم يظهر زخماً {'إيجابياً' if change_pct > 0 else 'سلبياً'}.
        """
        
        forecast_summary = f"{trend_signal} | هدف: {target_price:.2f}"
        print(f"   >> التنبؤ: {forecast_summary}")

    # 4. تحديث الحالة
    return {
        "technical_report": report,           # النص الكامل للتقرير
        "forecast_summary": forecast_summary, # ملخص سريع للمدير
        "forecast_data": result.get('raw_forecast') # البيانات الخام للرسم البياني
    }