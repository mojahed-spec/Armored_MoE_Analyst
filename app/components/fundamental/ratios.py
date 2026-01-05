import yfinance as yf
import pandas as pd
import numpy as np

class FinancialRatios:
    def __init__(self):
        pass

    def calculate_ratios(self, symbol: str) -> dict:
        """
        حساب النسب المالية المتقدمة لتقييم الأداء المالي.
        Returns:
            dict: يحتوي على نسب السيولة، الربحية، الملاءة، والسوق.
        """
        print(f"--- 📊 Ratios: حساب النسب المالية لـ {symbol} ---")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # حماية: إذا لم تتوفر البيانات
            if not info:
                return {"status": "error", "message": "بيانات غير متوفرة"}

            # 1. نسب التقييم (Valuation Ratios)
            # هل السهم رخيص أم غالي؟
            pe_ratio = info.get('trailingPE', 0)
            pb_ratio = info.get('priceToBook', 0)
            ps_ratio = info.get('priceToSalesTrailing12Months', 0)
            peg_ratio = info.get('pegRatio', 0) # مهم جداً للنمو

            # 2. نسب الربحية (Profitability Ratios)
            # كفاءة الشركة في توليد الأرباح
            roe = info.get('returnOnEquity', 0) # العائد على الملكية
            roa = info.get('returnOnAssets', 0) # العائد على الأصول
            profit_margin = info.get('profitMargins', 0)
            operating_margin = info.get('operatingMargins', 0)

            # 3. نسب السيولة (Liquidity Ratios)
            # قدرة الشركة على دفع ديونها قصيرة الأجل
            current_ratio = info.get('currentRatio', 0)
            quick_ratio = info.get('quickRatio', 0)

            # 4. نسب الملاءة/الديون (Solvency Ratios)
            # هل الشركة ستفلس على المدى الطويل؟
            debt_to_equity = info.get('debtToEquity', 0)
            interest_coverage = 0 # يحتاج حساب يدوي أحياناً من القوائم
            
            # محاولة حساب تغطية الفائدة يدوياً إذا توفرت البيانات
            try:
                financials = ticker.financials
                if not financials.empty:
                    ebit = financials.loc['Ebit'].iloc[0] if 'Ebit' in financials.index else 0
                    interest = financials.loc['Interest Expense'].iloc[0] if 'Interest Expense' in financials.index else 1
                    interest_coverage = abs(ebit / interest) if interest != 0 else 0
            except:
                pass

            # 5. التحليل الذكي (Ratio Interpretation)
            analysis = []
            
            # تحليل P/E
            if pe_ratio > 0:
                if pe_ratio < 15: analysis.append("سعر السهم منخفض (Undervalued).")
                elif pe_ratio > 30: analysis.append("سعر السهم مرتفع (Overvalued) أو نمو عالٍ.")
            
            # تحليل ROE
            if roe > 0.15: analysis.append("إدارة الشركة ممتازة في استثمار أموال المساهمين.")
            
            # تحليل الديون
            if debt_to_equity > 200: analysis.append("تحذير: ديون الشركة مرتفعة جداً.")

            return {
                "status": "success",
                "ratios": {
                    "P/E": round(pe_ratio, 2) if pe_ratio else "N/A",
                    "P/B": round(pb_ratio, 2) if pb_ratio else "N/A",
                    "PEG": round(peg_ratio, 2) if peg_ratio else "N/A",
                    "ROE": f"{roe*100:.2f}%" if roe else "N/A",
                    "ROA": f"{roa*100:.2f}%" if roa else "N/A",
                    "Profit Margin": f"{profit_margin*100:.2f}%" if profit_margin else "N/A",
                    "Current Ratio": round(current_ratio, 2) if current_ratio else "N/A",
                    "Debt/Equity": round(debt_to_equity, 2) if debt_to_equity else "N/A",
                    "Interest Coverage": round(interest_coverage, 2) if interest_coverage else "N/A"
                },
                "summary": " | ".join(analysis)
            }

        except Exception as e:
            return {"status": "error", "message": f"فشل حساب النسب: {str(e)}"}