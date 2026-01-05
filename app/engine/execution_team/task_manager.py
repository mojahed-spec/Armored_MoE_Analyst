from langgraph.graph import StateGraph, END
from app.engine.state import FinancialState

# استيراد جميع العمال (The Workers)
from app.engine.execution_team.workers.data_loader import DataLoader
from app.engine.execution_team.workers.defender import defender_node
from app.engine.execution_team.workers.fundamental import fundamental_analyst_node
from app.engine.execution_team.workers.technical import technical_analyst_node
from app.engine.execution_team.workers.researcher import researcher_node
from app.engine.execution_team.workers.writer import writer_node

# تغليف Loader ليعمل كعقدة (Node Wrapper)
loader = DataLoader()
def loader_node(state):
    print("--- 🏗️ Task Manager: تشغيل عامل التحميل ---")
    symbol = state.get('symbol')
    # نحاول تحميل بيانات سنة كاملة
    success, msg = loader.fetch_and_store_data(symbol, period="1y")
    
    if not success:
        return {"final_report": f"فشل تحميل البيانات: {msg}"}
        
    df = loader.get_data(symbol)
    return {"market_data": df}

class TaskManager:
    def __init__(self):
        self.workflow = self._build_execution_pipeline()

    def _build_execution_pipeline(self):
        """
        بناء خط التجميع (Assembly Line) لتنفيذ المهام.
        """
        workflow = StateGraph(FinancialState)
        
        # 1. إضافة العقد (Workers)
        workflow.add_node("loader", loader_node)
        workflow.add_node("defender", defender_node)
        workflow.add_node("fundamental", fundamental_analyst_node)
        workflow.add_node("technical", technical_analyst_node)
        workflow.add_node("researcher", researcher_node)
        workflow.add_node("writer", writer_node)
        
        # 2. رسم المسار (Logic Flow)
        # التسلسل المنطقي: بيانات -> حماية -> تحليل (متوازي نظرياً) -> كتابة
        
        # البداية: التحميل
        workflow.set_entry_point("loader")
        
        # بعد التحميل -> اذهب للدفاع
        workflow.add_edge("loader", "defender")
        
        # بعد الدفاع -> شغل المحللين الثلاثة (يمكن تشغيلهم بالتوالي في LangGraph البسيط)
        workflow.add_edge("defender", "fundamental")
        workflow.add_edge("fundamental", "technical")
        workflow.add_edge("technical", "researcher")
        
        # بعد انتهاء الجميع -> اذهب للكاتب
        workflow.add_edge("researcher", "writer")
        
        # النهاية
        workflow.add_edge("writer", END)
        
        return workflow.compile()

    def execute_plan(self, initial_state):
        """
        تشغيل الفريق لتنفيذ المهمة.
        """
        print("--- ⚙️ Task Manager: بدء تنفيذ الخطة التشغيلية ---")
        return self.workflow.invoke(initial_state)