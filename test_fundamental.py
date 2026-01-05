from app.components.fundamental.metrics import FundamentalMetrics

# إنشاء الأداة
analyzer = FundamentalMetrics()

# نجرب على سهم معروف (مثل تسلا)
symbol = "TSLA"
print(f"🚀 جاري تحليل القوائم المالية لـ {symbol}...")

# استدعاء الدالة
result = analyzer.get_key_metrics(symbol)

# عرض النتائج
if result.get('status') == 'success':
    print("\n✅ تم جلب البيانات بنجاح:")
    print("-" * 40)
    print(f"🔹 القطاع: {result.get('sector')}")
    print(f"💰 السعر الحالي: {result['valuation'].get('Current_Price')}")
    print(f"📉 مكرر الربحية (P/E): {result['valuation'].get('Trailing_PE')}")
    print(f"🛡️ نسبة الديون: {result['health'].get('Debt_to_Equity')}")
    print("-" * 40)
    print(f"📊 تقييم النظام (Score): {result.get('fundamental_score')}/3")
    print(f"📝 الخلاصة: {result.get('analysis_summary')}")
else:
    print(f"❌ خطأ: {result.get('message')}")