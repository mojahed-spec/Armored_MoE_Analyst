from app.components.research.sentiment import SentimentEngine

# تهيئة المحرك مرة واحدة لسرعة الاستجابة
sentiment_engine = SentimentEngine()

# 🔴 التعديل: تغيير الاسم ليتطابق مع workflow.py
def sentiment_node(state):
    """
    عامل تحليل المشاعر (Sentiment Analyst Worker).
    المهمة: قراءة الأخبار وتحديد هل السوق متفائل (Bullish) أم متشائم (Bearish).
    """
    print("--- 📰 Sentiment Analyst: قراءة نبض السوق ---")
    
    symbol = state.get('symbol')
    
    if not symbol:
        return {
            "sentiment_report": {
                "score": 0, 
                "summary": "خطأ: لا يوجد رمز للبحث."
            }
        }

    # 1. تشغيل المحرك (البحث + التحليل بالذكاء الاصطناعي)
    score, reason = sentiment_engine.analyze(symbol)
    
    # 2. تصنيف النتيجة
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
        "summary": reason,
    }

    # 4. تحديث الحالة
    return {
        "sentiment_report": report_data
    }