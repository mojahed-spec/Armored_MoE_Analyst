from typing import TypedDict, List, Annotated, Optional, Dict, Any
import pandas as pd
import operator
from langchain_core.messages import BaseMessage

class FinancialState(TypedDict):
    """
    الذاكرة المشتركة للنظام (Shared State).
    هنا يتم تخزين كل معلومة يكتشفها العمال أو يقررها المدراء.
    """
    
    # --- 1. ذاكرة المحادثة (Chat History) ---
    # نستخدم operator.add لكي لا نمسح الرسائل السابقة بل نضيف عليها
    messages: Annotated[List[BaseMessage], operator.add]
    
    # --- 2. سياق الطلب (Context) ---
    symbol: str                # الرمز (مثلاً: AAPL)
    sector: str                # القطاع (يحدده المدير، مثلاً: Technology)
    user_request: str          # ماذا يريد المستخدم بالضبط؟
    
    # --- 3. البيانات الخام (Raw Data) ---
    market_data: Optional[pd.DataFrame]  # جدول الأسعار التاريخي
    
    # --- 4. تقارير العمال (Worker Outputs) ---
    # كل عامل يملأ خانته الخاصة
    fundamental_data: Dict[str, Any]     # (P/E, Revenue Growth, Debt)
    technical_report: str                # (Trend, Support/Resistance)
    sentiment_report: Dict[str, Any]     # (Score, Summary, News)
    risk_report: Dict[str, Any]          # (Crash Probability, Anomalies)
    
    # --- 5. التحكم والإدارة (Control Flow) ---
    plan: List[str]            # خطة العمل التي وضعها المدير (قائمة العمال المطلوبين)
    current_step: str          # أين نحن الآن؟
    
    # --- 6. حلقة النقد والجودة (Quality Loop) ---
    draft_report: str          # المسودة الأولية
    review_status: str         # (APPROVED / REJECTED)
    feedback: str              # ملاحظات الناقد لإصلاح التقرير
    retry_count: int           # كم مرة حاولنا؟ (لمنع التكرار اللانهائي)
    # 👇 هذا هو المتغير الذي يحتاجه المخطط الجديد ليعمل
    is_quality_passed: bool 
    critic_feedback: str    # لتخزين ملاحظات الناقد
    # --- 7. المخرج النهائي ---
    final_report: str          # التقرير النهائي المعتمد