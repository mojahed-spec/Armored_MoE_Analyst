import json
import os
from typing import Dict, Any

# مسار ملف الذاكرة الاستراتيجية
MEMORY_FILE = "cache/strategy_memory.json"

class StrategyMemoryManager:
    def __init__(self):
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict:
        """تحميل الذاكرة من القرص الصلب"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Memory Warning: فشل تحميل الذاكرة ({e})، سيتم إنشاء ذاكرة جديدة.")
                return {}
        return {}

    def _save_memory(self):
        """حفظ الذاكرة لضمان الاستمرارية"""
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def get_past_strategy(self, sector: str) -> str:
        """
        استرجاع آخر استراتيجية ناجحة تم استخدامها لهذا القطاع.
        """
        # نبحث في سجلات القطاع
        sector_data = self.memory.get(sector)
        if sector_data and "last_successful_plan" in sector_data:
            return sector_data["last_successful_plan"]
        return None

    def update_strategy(self, sector: str, plan_summary: str):
        """
        تحديث الذاكرة بمعلومات جديدة بعد نجاح عملية تحليل.
        """
        if sector not in self.memory:
            self.memory[sector] = {}
        
        # نحدث آخر خطة
        self.memory[sector]["last_successful_plan"] = plan_summary
        self.memory[sector]["last_updated"] = "Recently" # يمكن استخدام datetime هنا
        
        # حفظ التغييرات
        self._save_memory()
        print(f"💾 Memory: تم تحديث الذاكرة الاستراتيجية لقطاع {sector}.")

# إنشاء نسخة جاهزة للاستخدام
memory_manager = StrategyMemoryManager()