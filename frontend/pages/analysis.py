import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. إصلاح المسارات لرؤية مجلد app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.engine.workflow import create_workflow

# --- إعداد الصفحة ---
st.set_page_config(page_title="التحليل المالي العميق", layout="wide", page_icon="📈")

# CSS للتصميم الداكن والاحترافي
st.markdown("""
<style>
    .main { direction: rtl; }
    .stTextInput > div > div > input { text-align: right; }
    
    /* تنسيق كروت المعلومات */
    .metric-container {
        background-color: #262730;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* تنسيق التقرير */
    .report-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.8;
        color: #f0f2f6;
        background-color: #1e1e1e;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #00c853;
    }
    
    h1, h2, h3 { text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("📈 منصة التحليل المالي المتعمق")
st.caption("تحليل مؤسساتي شامل: أساسي + فني + مشاعر + مخاطر")

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("إعدادات العملية")
    symbol = st.text_input("رمز السهم (Ticker):", "AAPL").upper()
    st.info("💡 نصيحة: استخدم الرموز العالمية (TSLA, NVDA) أو المحلية (2222.SR).")
    
    st.divider()
    st.write("**الأدوات النشطة:**")
    st.checkbox("التحليل الأساسي (Fundamental)", value=True, disabled=True)
    st.checkbox("التحليل الفني (Technical)", value=True, disabled=True)
    st.checkbox("تحليل الأخبار (Sentiment)", value=True, disabled=True)
    st.checkbox("حماية البيانات (Defender)", value=True, disabled=True)

# --- زر التشغيل ---
if st.button("🚀 بدء التحليل الشامل", use_container_width=True):
    
    with st.spinner(f'جاري استدعاء فريق التحليل للسهم {symbol}... يرجى الانتظار'):
        try:
            # 1. تشغيل المحرك
            app = create_workflow()
            inputs = {"symbol": symbol, "user_request": "تحليل شامل وعميق"}
            result = app.invoke(inputs)
            
            # التحقق من نجاح جلب البيانات
            if result.get('market_data') is None:
                st.error(f"❌ لم يتم العثور على بيانات للسهم {symbol}. يرجى التأكد من صحة الرمز.")
                st.stop()

            # 2. استخراج البيانات
            hist_df = result.get('market_data')
            forecast_df = result.get('forecast_data')
            report = result.get('final_report', 'لا يوجد تقرير.')
            
            # بيانات المشاعر
            sent_data = result.get('sentiment_report', {})
            if isinstance(sent_data, dict):
                sent_score = sent_data.get('score', 0)
                sent_label = sent_data.get('label', 'محايد')
            else:
                sent_score = 0
                sent_label = "غير معروف"

            # بيانات التحليل الأساسي
            fund_data = result.get('fundamental_data', {})
            if fund_data and isinstance(fund_data, dict):
                valuation = fund_data.get('valuation', {})
                pe_ratio = valuation.get('Trailing_PE', 'N/A')
                pb_ratio = valuation.get('Price_to_Book', 'N/A')
                fund_score = fund_data.get('fundamental_score', 0)
            else:
                pe_ratio = "N/A"
                pb_ratio = "N/A"
                fund_score = 0

            # --- 3. لوحة العرض (Dashboard) ---
            
            # A. شريط المؤشرات العلوية (KPIs)
            st.subheader("نظرة عامة سريعة")
            col1, col2, col3, col4 = st.columns(4)
            
            current_price = hist_df['close'].iloc[-1]
            
            col1.metric("السعر الحالي", f"${current_price:.2f}")
            col2.metric("مؤشر المشاعر", f"{sent_score}", sent_label)
            col3.metric("التقييم المالي", f"{fund_score}/3", help="بناءً على الربحية والديون والنمو")
            col4.metric("مكرر الربحية (P/E)", f"{pe_ratio}")

            # B. الرسم البياني المتقدم (Chart)
            st.subheader(f"التحليل الفني والاتجاه: {symbol}")
            
            # تجهيز البيانات
            hist_df['date'] = pd.to_datetime(hist_df['date'])
            
            fig = go.Figure()
            
            # الشموع اليابانية للتاريخ
            fig.add_trace(go.Candlestick(
                x=hist_df['date'],
                open=hist_df['open'], high=hist_df['high'],
                low=hist_df['low'], close=hist_df['close'],
                name='السعر التاريخي'
            ))
            
            # خط التوقعات (إذا وجد)
            if forecast_df is not None:
                # نحتاج لربط آخر نقطة حقيقية بأول نقطة توقع ليكون الخط متصلاً
                last_date = hist_df['date'].iloc[-1]
                last_val = hist_df['close'].iloc[-1]
                
                # إضافة نقطة الربط
                forecast_x = [last_date] + list(forecast_df['ds'])
                forecast_y = [last_val] + list(forecast_df['AutoARIMA'])
                
                fig.add_trace(go.Scatter(
                    x=forecast_x, 
                    y=forecast_y,
                    mode='lines+markers',
                    name='توقعات AI (7 أيام)',
                    line=dict(color='#FFA500', width=3, dash='dot')
                ))

            fig.update_layout(
                template="plotly_dark",
                height=550,
                xaxis_rangeslider_visible=False,
                title="حركة السعر والتنبؤات المستقبلية",
                yaxis_title="السعر (USD/SAR)"
            )
            st.plotly_chart(fig, use_container_width=True)

            # C. التقرير التفصيلي
            st.markdown("---")
            st.subheader("📄 التقرير الاستراتيجي الموحد")
            
            # عرض التقرير داخل صندوق منسق
            st.markdown(f"""
            <div class="report-text">
            {report.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            # زر التحميل (إضافي)
            st.download_button(
                label="📥 تحميل التقرير (TXT)",
                data=report,
                file_name=f"{symbol}_analysis_report.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"حدث خطأ غير متوقع: {e}")
            # لغرض التصحيح (Debugging)
            import traceback
            st.text(traceback.format_exc())