import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Bitcoin Halving Strategy", layout="wide")
st.markdown("<style>.stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }</style>", unsafe_allow_html=True)

# --- 2. 데이터 가져오기 (Yahoo Finance 사용 - 훨씬 안정적) ---
@st.cache_data(ttl=3600)
def get_historical_data():
    try:
        # 비트코인 과거 데이터 가져오기
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period="max")
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_live_price():
    try:
        btc = yf.Ticker("BTC-USD")
        return btc.fast_info['last_price']
    except:
        return 0.0

# --- 3. 전략 로직 ---
HALVINGS = [datetime(2012,11,28), datetime(2016,7,9), datetime(2020,5,11), datetime(2024,4,20)]
CURRENT_H = HALVINGS[-1]
TODAY = datetime.now()
diff = relativedelta(TODAY, CURRENT_H)
months_passed = diff.years * 12 + diff.months

# Zone 판별
if months_passed <= 12:
    zone, color, desc = "HOLDING ZONE", "#3498db", "현금화 준비 중 (H+12까지 관망)"
elif 12 < months_passed <= 18:
    zone, color, desc = "SELL ZONE", "#e74c3c", "분할 매도 및 수익 실현 구간"
elif 18 < months_passed <= 30:
    zone, color, desc = "CASH ZONE", "#f1c40f", "현금 보유하며 저점 대기 (가장 힘든 기다림)"
else:
    zone, color, desc = "BUY ZONE", "#2ecc71", "적극적 매수 및 수량 확보 구간"

# --- 4. 화면 구성 ---
st.title("₿ Bitcoin Halving 'The Formula'")
live_p = get_live_price()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${live_p:,.0f}")
c2.metric("Market Status", zone)
c3.metric("Months since H", f"{months_passed} Mo")
c4.metric("Next Halving", "~April 2028")

st.info(f"**Current Guidance:** {desc}")

# --- 5. 차트 그리기 ---
df_hist = get_historical_data()
if not df_hist.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['close'], name="BTC Price", line=dict(color='#f39c12')))
    
    for h in HALVINGS:
        fig.add_vline(x=h, line_width=1.5, line_dash="dash", line_color="gray")
    
    fig.update_layout(title="BTC All-Time Price (Log Scale)", yaxis_type="log", template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- 6. 이미지 데이터 기반 테이블 ---
st.divider()
t1, t2 = st.columns(2)
with t1:
    st.markdown("### 📋 Every Trade Produced")
    trades = {"Action": ["BUY", "SELL", "CASH", "BUY", "SELL", "CASH", "BUY", "SELL"],
              "Date": ["2015.05", "2018.01", "2018-19", "2019.01", "2021.11", "2021-22", "2022.11", "2025.10"],
              "Price": ["$237", "$13,500", "-", "$3,500", "$64,000", "-", "$16,500", "$108,000"]}
    st.table(pd.DataFrame(trades))

with t2:
    st.markdown("### 📊 Strategy vs Buy & Hold")
    math = {"Entry": ["2015 Bear", "2018 Bear", "2022 Bear"],
            "Strategy": ["$6,817,689", "$119,688", "$6,545"],
            "B&H": ["$286,920", "$19,429", "$4,121"]}
    st.table(pd.DataFrame(math))
