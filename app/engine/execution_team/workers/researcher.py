from app.components.research.sentiment import SentimentEngine

# تهيئة محرك المشاعر (Tavily + GPT) مرة واحدة
sentiment_engine = SentimentEngine()

def researcher_node(state):
    """
    عامل البحث (Researcher Worker).
    المهمة: مسح الأخبار الحديثة وتحديد "مزاج السوق" (Sentiment Analysis).
    """
    print("--- 📰 Researcher: البحث في الأخبار وتحليل المشاعر ---")
    
    symbol = state.get('symbol')
    
    if not symbol:
        return {"sentiment_report": {"score": 0, "summary": "لا يوجد رمز للبحث."}}

    # 1. تشغيل المحرك
    # (يعيد درجة رقمية + ملخص نصي للأسباب)
    score, reason = sentiment_engine.analyze(symbol)
    
    # 2. تفسير النتيجة (لجعلها مفهومة للمدير)
    label = "محايد 😐"
    if score >= 0.5:
        label = "إيجابي جداً (Bullish) 🟢"
    elif score > 0.1:
        label = "إيجابي بحذر 📈"
    elif score <= -0.5:
        label = "سلبي جداً (Bearish) 🔴"
    elif score < -0.1:
        label = "سلبي/قلق 📉"

    print(f"   >> نتيجة المشاعر: {score} ({label})")

    # 3. صياغة التقرير الإخباري
    report_data = {
        "score": score,
        "label": label,
        "summary": reason
    }

    # 4. تحديث الحالة
    return {
        "sentiment_report": report_data
    }