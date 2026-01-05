from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

# نستخدم درجة حرارة 0 ليكون النقد صارماً ومنطقياً بحتاً
llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0.0)

def critic_node(state):
    """
    عقدة الناقد (The Critic Node).
    المهمة: مراجعة جودة التقرير المبدئي قبل تسليمه للعميل.
    """
    print("--- 🧐 Critic: مراجعة جودة التقرير ---")
    
    # 1. استلام المسودة
    draft = state.get('draft_report')
    symbol = state.get('symbol')
    
    if not draft:
        return {"review_status": "REJECTED", "feedback": "لا يوجد تقرير للمراجعة!"}

    # 2. هندسة أمر المراجعة (Quality Assurance Prompt)
    prompt = PromptTemplate.from_template("""
    أنت مدير الجودة في شركة استشارات مالية.
    لديك مسودة تقرير عن سهم {symbol}.
    
    المسودة:
    {draft}
    
    المطلوب:
    قم بتقييم التقرير بناءً على المعايير التالية:
    1. هل يحتوي على توصية واضحة (شراء/بيع/انتظار)؟
    2. هل يغطي الجانب المالي (Fundamental) والفني (Technical)؟
    3. هل يذكر المخاطر بوضوح؟
    4. هل اللغة احترافية وموضوعية؟
    
    إذا كان التقرير جيداً، اكتب كلمة "APPROVED" في البداية.
    إذا كان ضعيفاً أو ناقصاً، اكتب "REJECTED" ثم اذكر السبب في سطر جديد.
    """)
    
    # 3. تشغيل الناقد
    chain = prompt | llm
    result = chain.invoke({"symbol": symbol, "draft": draft})
    review = result.content.strip()
    
    # 4. اتخاذ القرار
    status = "APPROVED"
    feedback = "تم الاعتماد."
    
    if "REJECTED" in review:
        status = "REJECTED"
        # استخراج سبب الرفض (ما بعد الكلمة الأولى)
        feedback = review.replace("REJECTED", "").strip()
        print(f"   ❌ تم رفض المسودة. السبب: {feedback[:50]}...")
    else:
        print("   ✅ تم اعتماد التقرير.")

    # 5. تحديث الحالة
    # نزيد عداد المحاولات لمنع الدوران اللانهائي (Infinite Loop)
    current_retries = state.get('retry_count', 0)
    
    return {
        "review_status": status,
        "feedback": feedback,
        "retry_count": current_retries + 1
    }