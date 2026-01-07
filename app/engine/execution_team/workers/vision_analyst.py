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
    vision_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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
    
    # التأكد من استدعاء الموديل داخل الدالة
    response = vision_model.invoke([msg])

    # 1. فحص الرد للتأكد أنه ليس None (تجنب خطأ attribute 'strip')
    if response is None or not hasattr(response, 'content') or not response.content:
        print("⚠️ Vision: الرد فارغ تماماً")
        return {
            "final_report": "❌ فشل الاتصال بالذكاء الاصطناعي أو الصورة غير مدعومة.",
            "is_quality_passed": True 
        }

    # 2. تنظيف النص بأمان
    content = str(response.content).strip()
    raw_content = content.replace("```json", "").replace("```", "").strip()

    try:
        import json
        data = json.loads(raw_content)
        
        # 3. استخراج الرمز مع فحص حالة الأحرف (symbol أو Symbol)
        extracted_symbol = data.get("Symbol") or data.get("symbol")
        
        if not extracted_symbol or str(extracted_symbol).lower() == "null":
             return {
                "final_report": f"⚠️ تم تحليل الصورة ولكن لم أجد رمز سهم واضح. الرد كان: {content}",
                "is_quality_passed": True
             }

        # نجاح العملية وتمرير البيانات للـ Loader
        return {
            "trade_ticket_data": data,
            "symbol": extracted_symbol,
            "is_quality_passed": False # السماح للـ Loader والعمال بالعمل
        }

    except Exception as e:
        # في حال كانت الصورة "قطة" أو أي شيء ليس JSON
        print(f"--- فشل تحليل JSON: {e} ---")
        return {
            "final_report": f"🧐 هذه الصورة لا تحتوي على بيانات صفقة منظمة. وصف الذكاء الاصطناعي للصورة: {content}",
            "is_quality_passed": True 
        }