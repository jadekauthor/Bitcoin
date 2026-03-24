import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 데이터 로드 함수 ---
@st.cache_data(ttl=3600)
def get_historical_data():
    try:
        df = yf.download("BTC-USD", period="max", interval="1d")
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 2. 반감기 및 전략 날짜 설정 ---
HALVINGS = [
    datetime(2012, 11, 28),
    datetime(2016, 7, 9),
    datetime(2020, 5, 11),
    datetime(2024, 4, 20)
]

# --- 3. 차트 생성 로직 ---
def create_strategy_chart(df):
    fig = go.Figure()

    # 메인 가격 선 (로그 스케일)
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['close'], 
        name="BTC Price", 
        line=dict(color='#f39c12', width=2)
    ))

    for h in HALVINGS:
        # 1. 반감기 본 날짜 (White)
        fig.add_vline(x=h, line_width=2, line_dash="solid", line_color="white")
        fig.add_annotation(x=h, y=0, text="Halving", showarrow=False, yref="paper", font=dict(color="white"))

        # 2. H + 18개월 (SELL - Red)
        sell_date = h + relativedelta(months=18)
        if sell_date < datetime.now() + relativedelta(years=2): # 미래 너무 먼 날짜 방지
            fig.add_vline(x=sell_date, line_width=2, line_dash="dash", line_color="#e74c3c")
            fig.add_annotation(x=sell_date, y=0.95, text="SELL (H+18)", showarrow=False, yref="paper", font=dict(color="#e74c3c"))

        # 3. H + 30개월 (BUY - Green)
        buy_date = h + relativedelta(months=30)
        if buy_date < datetime.now() + relativedelta(years=2):
            fig.add_vline(x=buy_date, line_width=2, line_dash="dash", line_color="#2ecc71")
            fig.add_annotation(x=buy_date, y=0.05, text="BUY (H+30)", showarrow=False, yref="paper", font=dict(color="#2ecc71"))

    fig.update_layout(
        title="Bitcoin Strategy: Halving, Sell(H+18), and Buy(H+30)",
        yaxis_type="log",
        template="plotly_dark",
        xaxis_title="Year",
        yaxis_title="Price (USD)",
        height=600,
        showlegend=False
    )
    return fig

# --- 4. 메인 실행부 ---
st.set_page_config(page_title="BTC Strategy Chart", layout="wide")
st.title("📈 The Formula: Halving Cycle Visualization")

df_hist = get_historical_data()

if not df_hist.empty:
    strategy_fig = create_strategy_chart(df_hist)
    st.plotly_chart(strategy_fig, use_container_width=True)
    
    st.markdown("""
    - **흰색 실선**: 반감기(Halving) 당일
    - **빨간색 점선 (H+18)**: 역사적 고점 부근 (매도 시점)
    - **초록색 점선 (H+30)**: 역사적 저점 부근 (매수 시점)
    """)
else:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
