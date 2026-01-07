import yfinance as yf
import pandas as pd
from typing import Dict, Any

class FundamentalMetrics:
    def __init__(self):
        pass

    def get_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        جلب المؤشرات المالية الأساسية (Fundamental Ratios)
        لتقييم صحة الشركة وقيمتها العادلة.
        """
        print(f"--- 📊 Fundamental: جلب القوائم المالية لـ {symbol} ---")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # في حال فشل الجلب أو الرمز خاطئ
            if not info or 'regularMarketPrice' not in info:
                # محاولة ثانية للتأكد (أحياناً yfinance يعيد قاموساً فارغاً أول مرة)
                info = ticker.info
                if not info:
                    return {"status": "error", "message": "لم يتم العثور على بيانات مالية"}

            # 1. مؤشرات التقييم (Valuation) - هل السهم رخيص أم غالي؟
            valuation = {
                "Current_Price": info.get('currentPrice'),
                "Market_Cap": info.get('marketCap'),
                "Trailing_PE": info.get('trailingPE'), # مكرر الربحية الحالي
                "Forward_PE": info.get('forwardPE'),   # مكرر الربحية المستقبلي
                "PEG_Ratio": info.get('pegRatio'),     # السعر بالنسبة للنمو (مهم جداً)
                "Price_to_Book": info.get('priceToBook') # القيمة الدفترية
            }

            # 2. مؤشرات الربحية (Profitability) - هل الشركة تكسب مالاً؟
            profitability = {
                "Profit_Margin": info.get('profitMargins'), # هامش الربح الصافي
                "Operating_Margin": info.get('operatingMargins'),
                "ROE": info.get('returnOnEquity'), # العائد على حقوق المساهمين (الكفاءة)
                "ROA": info.get('returnOnAssets')
            }

            # 3. الصحة المالية (Financial Health) - هل ستفلس قريباً؟
            health = {
                "Total_Debt": info.get('totalDebt'),
                "Debt_to_Equity": info.get('debtToEquity'), # نسبة الديون للملكية
                "Current_Ratio": info.get('currentRatio'),  # القدرة على سداد الديون القصيرة
                "Free_Cash_Flow": info.get('freeCashflow')  # الكاش الحر (شريان الحياة)
            }

            # 4. النمو (Growth) - هل الشركة تكبر أم تموت؟
            growth = {
                "Revenue_Growth": info.get('revenueGrowth'),
                "Earnings_Growth": info.get('earningsGrowth')
            }

            # 5. التقييم الذكي (حكم بسيط)
            # نقوم بحساب "نقاط قوة" بسيطة
            score = 0
            analysis_notes = []

            # قاعدة 1: الربحية
            if profitability['Profit_Margin'] and profitability['Profit_Margin'] > 0.15:
                score += 1
                analysis_notes.append("ربحية ممتازة (هامش صافي > 15%).")
            elif profitability['Profit_Margin'] and profitability['Profit_Margin'] < 0:
                score -= 1
                analysis_notes.append("الشركة تحقق خسائر (هامش سالب).")

            # قاعدة 2: التقييم
            if valuation['Forward_PE'] and valuation['Forward_PE'] < 20:
                score += 1
                analysis_notes.append("سعر السهم يعتبر جذاباً مقارنة بالأرباح المتوقعة.")
            
            # قاعدة 3: الديون
            if health['Debt_to_Equity'] and health['Debt_to_Equity'] > 200:
                score -= 1
                analysis_notes.append("مخاطر عالية: الشركة مثقلة بالديون.")

            return {
                "status": "success",
                "symbol": symbol,
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "valuation": valuation,
                "profitability": profitability,
                "health": health,
                "growth": growth,
                "fundamental_score": score, # من -2 إلى +3 تقريباً
                "analysis_summary": " | ".join(analysis_notes)
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

class FundamentalMetrics:
    def __init__(self):
        pass

    def get_key_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        جلب المؤشرات المالية الأساسية (Fundamental Ratios)
        لتقييم صحة الشركة وقيمتها العادلة.
        """
        print(f"--- 📊 Fundamental: جلب القوائم المالية لـ {symbol} ---")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # في حال فشل الجلب أو الرمز خاطئ
            if not info or 'regularMarketPrice' not in info:
                # محاولة ثانية للتأكد
                info = ticker.info
                if not info:
                    return {"status": "error", "message": "لم يتم العثور على بيانات مالية"}

            # 1. مؤشرات التقييم
            valuation = {
                "Current_Price": info.get('currentPrice'),
                "Market_Cap": info.get('marketCap'),
                "Trailing_PE": info.get('trailingPE'),
                "Forward_PE": info.get('forwardPE'),
                "PEG_Ratio": info.get('pegRatio'),
                "Price_to_Book": info.get('priceToBook')
            }

            # 2. مؤشرات الربحية
            profitability = {
                "Profit_Margin": info.get('profitMargins'),
                "Operating_Margin": info.get('operatingMargins'),
                "ROE": info.get('returnOnEquity'),
                "ROA": info.get('returnOnAssets')
            }

            # 3. الصحة المالية
            health = {
                "Total_Debt": info.get('totalDebt'),
                "Debt_to_Equity": info.get('debtToEquity'),
                "Current_Ratio": info.get('currentRatio'),
                "Free_Cash_Flow": info.get('freeCashflow')
            }

            # 4. النمو
            growth = {
                "Revenue_Growth": info.get('revenueGrowth'),
                "Earnings_Growth": info.get('earningsGrowth')
            }

            # 5. التقييم الذكي
            score = 0
            analysis_notes = []

            if profitability['Profit_Margin'] and profitability['Profit_Margin'] > 0.15:
                score += 1
                analysis_notes.append("ربحية ممتازة (هامش صافي > 15%).")
            elif profitability['Profit_Margin'] and profitability['Profit_Margin'] < 0:
                score -= 1
                analysis_notes.append("الشركة تحقق خسائر (هامش سالب).")

            if valuation['Forward_PE'] and valuation['Forward_PE'] < 20:
                score += 1
                analysis_notes.append("سعر السهم يعتبر جذاباً مقارنة بالأرباح المتوقعة.")
            
            if health['Debt_to_Equity'] and health['Debt_to_Equity'] > 200:
                score -= 1
                analysis_notes.append("مخاطر عالية: الشركة مثقلة بالديون.")

            return {
                "status": "success",
                "symbol": symbol,
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "valuation": valuation,
                "profitability": profitability,
                "health": health,
                "growth": growth,
                "fundamental_score": score,
                "analysis_summary": " | ".join(analysis_notes)
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}