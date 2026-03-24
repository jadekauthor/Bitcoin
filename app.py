import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="BTC Cycle Dashboard", layout="wide")

# --- 2. 데이터 로드 함수 (오류 방지 강화) ---
@st.cache_data(ttl=3600)
def get_crypto_data():
    try:
        # Ticker 객체를 통해 개별 데이터 추출 시도
        data = yf.download("BTC-USD", start="2010-01-01", end=datetime.now().strftime('%Y-%m-%d'), progress=False)
        if data.empty:
            return pd.DataFrame()
        df = data.reset_index()
        df.columns = [str(c).lower() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 3. 기본 정보 설정 ---
HALVINGS = [datetime(2012,11,28), datetime(2016,7,9), datetime(2020,5,11), datetime(2024,4,20)]
TODAY = datetime.now()

# --- 4. 메인 화면 ---
st.title("₿ Bitcoin Halving 'The Formula'")

df_hist = get_crypto_data()

# 데이터가 비어있을 경우 예외 처리
if df_hist.empty:
    st.error("⚠️ 외부 데이터(Yahoo Finance) 연결에 실패했습니다.")
    st.info("임시 시세로 대시보드를 표시합니다. 잠시 후 새로고침(F5) 해주세요.")
    current_price = 95000.0  # 데이터 못 불러올 때 임시 표시 가격
else:
    current_price = df_hist['close'].iloc[-1]

# --- 5. 대시보드 상단 지표 ---
c1, c2, c3 = st.columns(3)
c1.metric("Current Price", f"${float(current_price):,.0f}")
c2.metric("Market Status", "CASH PHASE (WAITING)")
c3.metric("Next Halving", "~April 2028")

# --- 6. 차트 구성 ---
if not df_hist.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['close'], name="BTC", line=dict(color='#f39c12')))

    for h in HALVINGS:
        # Halving (White)
        fig.add_vline(x=h, line_width=1, line_color="white", opacity=0.5)
        # SELL (H+18)
        s_date = h + relativedelta(months=18)
        fig.add_vline(x=s_date, line_width=2, line_dash="dash", line_color="#e74c3c")
        # BUY (H+30)
        b_date = h + relativedelta(months=30)
        fig.add_vline(x=b_date, line_width=2, line_dash="dash", line_color="#2ecc71")

    fig.update_layout(yaxis_type="log", template="plotly_dark", height=500, title="BTC Log Chart with H+18 & H+30 Lines")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("데이터 로딩 중입니다... 깃허브에서 'Reboot App'을 누르거나 잠시만 기다려주세요.")

# --- 7. 이미지 기반 테이블 데이터 (항상 표시됨) ---
st.divider()
st.markdown("### 📋 Strategy Performance (The Formula)")
col_a, col_b = st.columns(2)
with col_a:
    st.write("**Every Trade Produced:**")
    st.table(pd.DataFrame({
        "Action": ["BUY", "SELL", "BUY", "SELL", "BUY", "SELL"],
        "Date": ["2015.05", "2018.01", "2019.01", "2021.11", "2022.11", "2025.10 (Exp)"],
        "BTC Price": ["$237", "$13,500", "$3,500", "$64,000", "$16,500", "$108,000"]
    }))
