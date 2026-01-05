from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

# نستخدم درجة حرارة منخفضة للدقة
llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0.3)

# 🔴 التعديل هنا: تغيير اسم الدالة من writer_node إلى reporter_node
def reporter_node(state):
    """
    عامل الكتابة (Reporter Worker).
    المهمة: تجميع تقارير الفريق وصياغة التقرير النهائي.
    """
    print("--- 📝 Reporter: صياغة التقرير النهائي الموحد ---")
    
    symbol = state.get('symbol')
    
    # جلب التقارير الفرعية
    fund_summary = state.get('fundamental_summary', 'بيانات أساسية غير متوفرة.')
    tech_report = state.get('technical_report', 'بيانات فنية غير متوفرة.')
    
    sent_data = state.get('sentiment_report', {})
    if isinstance(sent_data, dict):
        sent_summary = sent_data.get('summary', 'لا توجد أخبار.')
        sent_score = sent_data.get('score', 0)
    else:
        sent_summary = "بيانات المشاعر غير واضحة."
        sent_score = 0
    
    defense_summary = state.get('defense_report', 'لم يتم إجراء فحص أمني.')

    # هندسة الأمر
    prompt = PromptTemplate.from_template("""
    أنت رئيس قسم الأبحاث في مؤسسة مالية كبرى.
    لديك مسودات وتقارير من فريق التحليل بخصوص سهم: {symbol}.
    
    مهمتك: دمج هذه المعلومات المتفرقة في تقرير استثماري واحد، متماسك، واحترافي باللغة العربية.
    
    --- البيانات الواردة ---
    1. تقرير الأمان: {defense_summary}
    2. التحليل الأساسي: {fund_summary}
    3. التحليل الفني: {tech_report}
    4. تحليل الأخبار (Score: {sent_score}): {sent_summary}
    
    --- الهيكل المطلوب ---
    اكتب التقرير بتنسيق Markdown بالعناوين التالية:
    ### 📊 الملخص والتوصية
    (شراء/بيع/انتظار مع السبب).
    ### 🏢 الوضع المالي
    ### 📈 التوقيت الفني ونبض السوق
    ### ⚠️ المخاطر
    """)
    
    chain = prompt | llm
    result = chain.invoke({
        "symbol": symbol,
        "defense_summary": defense_summary,
        "fund_summary": fund_summary,
        "tech_report": tech_report,
        "sent_summary": sent_summary,
        "sent_score": sent_score
    })
    
    final_text = result.content
    
    return {
        "final_report": final_text 
    }