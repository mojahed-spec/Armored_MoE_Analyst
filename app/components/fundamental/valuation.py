import yfinance as yf
import pandas as pd
import numpy as np

class ValuationModel:
    def __init__(self):
        pass

    def calculate_dcf(self, symbol: str, discount_rate=0.10, terminal_growth_rate=0.025, projection_years=5) -> dict:
        """
        حساب القيمة العادلة للسهم باستخدام نموذج التدفقات النقدية المخصومة (Simplified DCF).
        
        Args:
            symbol: رمز السهم.
            discount_rate: معدل الخصم (WACC تقريبي، الافتراضي 10%).
            terminal_growth_rate: معدل النمو الأبدي (عادة 2-3%).
            projection_years: عدد سنوات التوقع المستقبلي.
        """
        print(f"--- 💎 Valuation: حساب القيمة العادلة (Intrinsic Value) لـ {symbol} ---")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 1. جلب بيانات التدفق النقدي (Free Cash Flow)
            cash_flow_stmt = ticker.cashflow
            if cash_flow_stmt.empty:
                 return {"status": "error", "message": "لا توجد بيانات تدفق نقدي متاحة لحساب القيمة."}
            
            # محاولة الحصول على FCF لآخر سنة مالية
            try:
                # نبحث عن الصف المسمى 'Free Cash Flow' أو نحسبه
                if 'Free Cash Flow' in cash_flow_stmt.index:
                    fcf_recent = cash_flow_stmt.loc['Free Cash Flow'].iloc[0]
                else:
                    # الحساب اليدوي: التدفق التشغيلي + النفقات الرأسمالية (عادة بالسالب)
                    operating_cashflow = cash_flow_stmt.loc['Total Cash From Operating Activities'].iloc[0]
                    capex = cash_flow_stmt.loc['Capital Expenditures'].iloc[0]
                    fcf_recent = operating_cashflow + capex 
            except:
                return {"status": "error", "message": "تعذر استخراج رقم التدفق النقدي الحر (FCF)."}

            # 2. تحديد معدل النمو (Growth Rate)
            # نستخدم توقعات نمو الأرباح كتقريب، مع وضع سقف للأمان
            growth_rate = info.get('earningsGrowth', 0.05)
            if growth_rate is None: growth_rate = 0.05
            
            # Safety Cap: لا نفترض نمواً خيالياً للأبد (نحده بـ 15% ليكون التحليل محافظاً)
            if growth_rate > 0.15: growth_rate = 0.15 

            # جلب عدد الأسهم
            shares_outstanding = info.get('sharesOutstanding')
            if not shares_outstanding:
                return {"status": "error", "message": "عدد الأسهم غير معروف."}

            # 3. عملية التنبؤ (Projection Phase)
            future_cash_flows = []
            current_fcf = fcf_recent
            
            for i in range(1, projection_years + 1):
                # زيادة الكاش بمعدل النمو
                current_fcf = current_fcf * (1 + growth_rate)
                # خصم القيمة لتعود لقيمتها اليوم (Discounting)
                discounted_fcf = current_fcf / ((1 + discount_rate) ** i)
                future_cash_flows.append(discounted_fcf)

            # 4. القيمة النهائية (Terminal Value)
            # قيمة الشركة لما بعد سنوات التوقع (إلى الأبد)
            last_projected_fcf = current_fcf
            terminal_value = (last_projected_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
            discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)

            # 5. مجموع قيمة الشركة (Enterprise Value to Equity Value)
            total_value = sum(future_cash_flows) + discounted_terminal_value
            
            # تعديل القيمة بناءً على الكاش والديون (للحصول على قيمة حقوق المساهمين)
            balance_sheet = ticker.balance_sheet
            try:
                cash_and_equivalents = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
                total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else 0
                equity_value = total_value + cash_and_equivalents - total_debt
            except:
                # إذا لم تتوفر الميزانية بدقة، نستخدم القيمة المحسوبة كتقريب
                equity_value = total_value

            # 6. القيمة العادلة للسهم الواحد
            fair_value_per_share = equity_value / shares_outstanding
            current_price = info.get('currentPrice')

            # حساب هامش الأمان (Margin of Safety)
            # كم السعر الحالي أرخص من القيمة العادلة؟
            difference = fair_value_per_share - current_price
            margin_of_safety_pct = (difference / fair_value_per_share) * 100

            # الحكم النهائي
            valuation_status = "سعر عادل (Fair)"
            if current_price < fair_value_per_share * 0.7: # أرخص بـ 30%
                valuation_status = "أقل من قيمته (Undervalued) - فرصة جوهرية 💎"
            elif current_price > fair_value_per_share * 1.3: # أغلى بـ 30%
                valuation_status = "أعلى من قيمته (Overvalued) - تضخم سعري 🎈"

            return {
                "status": "success",
                "symbol": symbol,
                "current_price": current_price,
                "fair_value": round(fair_value_per_share, 2),
                "margin_of_safety": f"{margin_of_safety_pct:.2f}%",
                "valuation_status": valuation_status,
                "assumptions": {
                    "growth_used": f"{growth_rate*100:.1f}%",
                    "discount_rate": f"{discount_rate*100:.1f}%"
                }
            }

        except Exception as e:
            return {"status": "error", "message": f"خطأ في معادلة التقييم: {str(e)}"}