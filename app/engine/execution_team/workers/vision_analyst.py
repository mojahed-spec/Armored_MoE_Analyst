# app/engine/execution_team/workers/vision_analyst.py

import base64
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

def encode_image(image_path):
    """تحويل الصورة إلى Base64 ليفهمها النموذج"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def vision_node(state):
    print("--- 👁️ Vision Analyst: تحليل صورة الصفقة ---")
    
    image_path = state.get('screenshot_path')
    if not image_path:
        return {"trade_ticket_data": {"error": "No image provided"}}

    # 1. تجهيز النموذج (نحتاج موديل قوي للصور)
    vision_model = ChatOpenAI(model="gpt-4o", temperature=0)

    # 2. تحويل الصورة
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        return {"trade_ticket_data": {"error": f"Image load failed: {str(e)}"}}

    # 3. التعليمات الصارمة (System Prompt)
    prompt = """
    أنت خبير في قراءة منصات التداول (MetaTrader/TradingView).
    مهمتك استخراج بيانات الصفقة من الصورة بدقة متناهية.
    
    الحقول المطلوبة (JSON Format Only):
    - Order: رقم العملية (ID).
    - Type: نوع الصفقة (Buy/Sell).
    - Size: حجم اللوت (رقم عشري).
    - Symbol: زوج العملات (مثل EURUSD).
    - SL: سعر وقف الخسارة (إن وجد، وإلا null).
    - TP: سعر جني الأرباح (إن وجد، وإلا null).
    - Profit: الربح/الخسارة العائمة (مع الإشارة + أو -).
    
    ملاحظة: تجاهل أي نصوص أخرى غير ذات صلة.
    """

    # 4. استدعاء النموذج
    msg = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    
    response = vision_model.invoke([msg])
    
    # 5. تنظيف النتيجة وتحويلها لـ Dict
    # (هنا نفترض أن الموديل أرجع JSON، يمكن استخدام JsonOutputParser لضمان ذلك)
    raw_content = response.content.replace("```json", "").replace("```", "")
    
    import json
    try:
        data = json.loads(raw_content)
    except:
        data = {"raw_text": raw_content}

    print(f"✅ Vision: تم استخراج بيانات الصفقة {data.get('Order', 'Unknown')}")
    
    return {"trade_ticket_data": data}