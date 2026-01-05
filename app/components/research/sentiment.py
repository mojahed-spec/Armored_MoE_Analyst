import os
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

class SentimentEngine:
    def __init__(self):
        # التأكد من وجود المفاتيح قبل البدء
        if not settings.TAVILY_API_KEY:
            print("⚠️ تحذير: مفتاح Tavily غير موجود. تحليل المشاعر لن يعمل.")
            self.tavily = None
        else:
            self.tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
            
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)

    def analyze(self, symbol: str):
        """
        يقوم بالبحث عن أخبار السهم وتحليل مشاعر السوق تجاهه.
        Returns:
            score (float): من -1.0 (سلبي جداً) إلى 1.0 (إيجابي جداً)
            summary (str): ملخص للأسباب
        """
        print(f"--- 📰 Sentiment: جاري البحث عن أخبار {symbol} ---")
        
        if not self.tavily:
            return 0.0, "تعذر التحليل: مفتاح البحث غير متوفر."

        try:
            # 1. البحث في الويب (آخر 3 أيام للحصول على أخبار طازجة)
            # نستخدم كلمات مفتاحية دقيقة لتقليل الضوضاء
            query = f"{symbol} stock news market sentiment analysis financial reports"
            response = self.tavily.search(
                query=query, 
                topic="news", 
                days=3, 
                max_results=5
            )
            
            # تجميع محتوى الأخبار
            articles = [r['content'] for r in response['results']]
            news_text = "\n\n".join(articles)
            
            if not news_text:
                return 0.0, "لا توجد أخبار حديثة كافية للتحليل."

            # 2. التحليل باستخدام الذكاء الاصطناعي (LLM)
            # نستخدم Prompt هندسي دقيق للحصول على نتائج مهيكلة
            prompt = PromptTemplate.from_template("""
            أنت خبير مالي متخصص في تحليل سيكولوجية السوق (Market Sentiment).
            لديك ملخص لأحدث الأخبار عن سهم {symbol}:
            
            {news}
            
            المطلوب منك بدقة:
            1. حلل النبرة العامة (Tone) للأخبار: هل هي متفائلة (Bullish) أم متشائمة (Bearish) أم محايدة؟
            2. أعطني درجة رقمية دقيقة من -1.0 (انهيار/سلبي جداً) إلى 1.0 (نمو/إيجابي جداً).
            3. اكتب ملخصاً موجزاً (سطرين أو ثلاثة) يشرح السبب وراء تقييمك (ذكر الأحداث الرئيسية).
            
            تنسيق الإجابة المطلوب (التزم به حرفياً):
            SCORE: [الرقم هنا]
            REASON: [الملخص هنا]
            """)
            
            chain = prompt | self.llm
            result = chain.invoke({"symbol": symbol, "news": news_text})
            content = result.content
            
            # 3. استخراج النتائج (Parsing)
            score = 0.0
            reason = content
            
            for line in content.split('\n'):
                if "SCORE:" in line:
                    try:
                        score_str = line.replace("SCORE:", "").strip()
                        score = float(score_str)
                    except:
                        pass
                if "REASON:" in line:
                    reason = line.replace("REASON:", "").strip()
            
            return score, reason

        except Exception as e:
            print(f"❌ خطأ في تحليل المشاعر: {e}")
            return 0.0, f"حدث خطأ أثناء تحليل الأخبار: {str(e)}"