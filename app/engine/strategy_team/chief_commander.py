import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings

# مسار الذاكرة الدلالية (التي أنشأها المصنع)
SEMANTIC_CACHE_PATH = "cache/semantic_net.json"


class ChiefCommander:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)
        self.semantic_net = self._load_semantic_net()

    def _load_semantic_net(self):
        """تحميل خريطة العلاقات والقطاعات من الذاكرة"""
        if os.path.exists(SEMANTIC_CACHE_PATH):
            try:
                with open(SEMANTIC_CACHE_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ تحذير: فشل تحميل الشبكة الدلالية: {e}")
        return {}

    def identify_sector(self, symbol: str) -> str:
        """
        تحديد هوية الشركة وقطاعها بناءً على الذاكرة.
        """
        sectors = self.semantic_net.get("SECTORS", {})
        
        # 1. بحث مباشر
        if symbol in sectors:
            return sectors[symbol]
        
        # 2. تخمين ذكي (إذا لم تكن في الذاكرة)
        if "-" in symbol: return "CRYPTOCURRENCY" if "USD" in symbol else "FOREX"
        if symbol.endswith(".SR"): return "SAUDI_MARKET"
        
        return "UNKNOWN_SECTOR"

    def formulate_plan(self, symbol: str, sector: str, user_request: str) -> dict:
        """
        وضع خطة العمل (SOP) بناءً على القطاع.
        """
        print(f"--- 🧠 Chief Commander: تمييز الهدف {symbol} ({sector}) ---")
        
        # استراتيجية التحليل حسب القطاع
        # كل قطاع له "وصفة" خاصة
        focus_area = "تحليل عام"
        
        if sector == "EV_TECH" or sector == "SEMICONDUCTORS":
            focus_area = "التركيز على: النمو المستقبلي، الابتكار، والتقلبات العالية."
        elif sector == "ENERGY_OIL":
            focus_area = "التركيز على: التوزيعات النقدية، أسعار النفط، والاستقرار."
        elif sector == "CRYPTOCURRENCY":
            focus_area = "التركيز على: الزخم (Momentum)، الأخبار التنظيمية، والمخاطر العالية."

        # توجيهات للمحرر (Writer)
        guidelines = f"""
        - هذا السهم ينتمي لقطاع: {sector}.
        - استراتيجية التحليل المطلوبة: {focus_area}
        - طلب العميل الخاص: {user_request}
        """
        
        return {"sector": sector, "guidelines": guidelines}

# --- العقدة (Node Logic) ---

commander = ChiefCommander()

def chief_node(state):
    print("--- 👔 Strategy Team: وضع خطة التحليل ---")
    
    symbol = state.get('symbol')
    user_request = state.get('user_request', '')
    screenshot_path = state.get('screenshot_path') # 🟢 تأكد من استقبال مسار الصورة
    
    # ====================================================
    # 🛡️ منطقة الحماية (The Fix)
    # ====================================================
    
    # الحالة 1: يوجد صورة ولكن لا يوجد رمز سهم (لم يتم التحليل بعد)
    if not symbol and screenshot_path:
        print("📸 Chief: تم استلام صورة.. جاري تحويل المهمة للمحلل البصري فوراً.")
        # ننهي عمل المدير هنا ونمرر الدور للتالي (Vision) دون تشغيل identify_sector
        return {
            "current_step": "vision_analysis",
            # لا نعدل الرمز ولا القطاع، نتركهم كما هم
        }

    # الحالة 2: لا يوجد رمز ولا صورة (خطأ مستخدم)
    if not symbol:
        return {
            "draft_report": "⚠️ يرجى تزويدي باسم سهم أو صورة للتحليل.",
            "plan": [] # خطة فارغة
        }

    # ====================================================
    # المسار الطبيعي (يوجد رمز سهم)
    # ====================================================
    
    # 1. الفهم (الآن آمن لأن symbol ليس None)
    sector = commander.identify_sector(symbol)
    
    # 2. التخطيط
    plan_data = commander.formulate_plan(symbol, sector, user_request)
    
    # 3. إصدار الأوامر
    return {
        "sector": sector,
        "plan": ["loader", "defender", "fundamental", "technical", "researcher", "writer"],
        "current_step": "loader",
        "draft_report": f"ملاحظات إدارية: {plan_data['guidelines']}"
    }