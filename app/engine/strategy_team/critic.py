from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from langchain_core.messages import SystemMessage 
# نستخدم درجة حرارة 0 ليكون النقد صارماً ومنطقياً بحتاً
llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0.0)

def critic_node(state):
    print("--- 🧐 Critic: مراجعة جودة التقرير ---")
    
    # 1. استرجاع عدد المحاولات السابقة
    current_retries = state.get("retry_count", 0)
    
    # 🛑 قاطع الدائرة (Circuit Breaker): 
    # إذا تجاوزنا 3 محاولات، نقبل التقرير كما هو حتى لو كان سيئاً لمنع الانهيار
    if current_retries >= 3:
        print(f"   >> ⚠️ تجاوز حد المحاولات ({current_retries}). قبول التقرير قسراً.")
        return {
            "is_quality_passed": True, # نمرر التقرير لننهي العمل
            "feedback": "تم قبول التقرير لتجاوز عدد المحاولات المسموح بها."
        }

    report = state.get('final_report', '')
    symbol = state.get('symbol')

    # 2. التقييم
    prompt = f"""
    أنت مدقق جودة صارم. راجع هذا التقرير المالي عن {symbol}.
    
    المعايير المقبولة:
    1. هل يحتوي على سعر حالي أو تحليل فني؟
    2. هل يحتوي على توصية واضحة (شراء/بيع/احتفاظ)؟
    
    التقرير:
    {report}
    
    إذا كان التقرير "فارغاً" أو يقول "لا توجد بيانات"، وتكرر ذلك، فاقبله لإنهاء الدورة.
    هل التقرير مقبول؟ (نعم/لا) مع تعليل قصير.
    """
    
    # استدعاء الموديل
    response = llm.invoke([SystemMessage(content=prompt)])
    content = response.content.lower()
    
    # 3. القرار
    # نبحث عن كلمات الموافقة
    is_passed = "نعم" in content or "yes" in content or "مقبول" in content
    
    if is_passed:
        print("   >> ✅ التقرير مطابق للمعايير.")
        return {"is_quality_passed": True, "retry_count": 0}
    else:
        print(f"   >> ❌ تم رفض التقرير (المحاولة {current_retries + 1}). إعادة التوجيه للمحرر.")
        return {
            "is_quality_passed": False, 
            "feedback": response.content,
            "retry_count": current_retries + 1 # زيادة العداد لإخبار النظام
        }