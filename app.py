import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(page_title="Bitcoin Halving Strategy", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 가져오기 (실시간 시세 & 히스토리) ---
@st.cache_data(ttl=3600) # 차트 데이터는 1시간마다 업데이트
def get_historical_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "max", "interval": "daily"}
    res = requests.get(url, params=params).json()
    df = pd.DataFrame(res['prices'], columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

@st.cache_data(ttl=60) # 실시간 시세는 1분마다
def get_live_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
    return requests.get(url).json()['bitcoin']

# --- 3. 반감기 데이터 및 로직 ---
HALVINGS = [
    datetime(2012, 11, 28),
    datetime(2016, 7, 9),
    datetime(2020, 5, 11),
    datetime(2024, 4, 20)
]
CURRENT_H = HALVINGS[-1]
TODAY = datetime.now()

diff = relativedelta(TODAY, CURRENT_H)
months_passed = diff.years * 12 + diff.months

# Zone 판별 로직
if months_passed <= 12:
    zone, color, desc = "HOLDING ZONE", "#3498db", "현금화 준비 중 (H+12까지 관망)"
elif 12 < months_passed <= 18:
    zone, color, desc = "SELL ZONE / CASH OUT", "#e74c3c", "분할 매도 및 수익 실현 구간"
elif 18 < months_passed <= 30:
    zone, color, desc = "CASH ZONE (WAITING)", "#f1c40f", "현금 보유하며 저점 대기 (가장 힘든 기다림)"
else:
    zone, color, desc = "BUY ZONE", "#2ecc71", "적극적 매수 및 수량 확보 구간"

# --- 4. 메인 화면 구성 ---
st.title("₿ Bitcoin Halving 'The Formula' Dashboard")
st.subheader(f"Strategy by Bitcoin Jae | Today: {TODAY.strftime('%Y-%m-%d')}")

# 상단 지표
live = get_live_data()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${live['usd']:,.0f}", f"{live['usd_24h_change']:.2f}%")
c2.metric("Market Status", zone)
c3.metric("Months since H", f"{months_passed} Mo")
c4.metric("Next Halving", "~April 2028")

st.info(f"**Current Guidance:** {desc}")

# --- 5. 히스토리 차트 (반감기 표시) ---
df_hist = get_historical_data()
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['price'], name="BTC Price", line=dict(color='#f39c12')))

# 반감기 세로선 추가
for h in HALVINGS:
    fig.add_vline(x=h, line_width=2, line_dash="dash", line_color="white")
    fig.add_annotation(x=h, y=0, text="Halving", showarrow=True, arrowhead=1)

fig.update_layout(title="Bitcoin All-Time Price with Halving Events", yaxis_type="log", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# --- 6. 전략 정리 (이미지 내용 요약) ---
st.divider()
t1, t2 = st.columns(2)

with t1:
    st.markdown("### 📋 The Formula Produced")
    data_trades = {
        "Action": ["BUY", "SELL", "CASH", "BUY", "SELL", "CASH", "BUY", "SELL", "CASH"],
        "Date": ["May 2015", "Jan 2018", "18-19", "Jan 2019", "Nov 2021", "21-22", "Nov 2022", "Oct 2025", "25-Present"],
        "BTC Price": ["$237", "$13,500", "-", "$3,500", "$64,000", "-", "$16,500", "$108,000", "-"],
        "Trigger": ["H+30", "H+18", "12mo Cash", "H+30", "H+18", "12mo Cash", "H+30", "H+18", "Waiting"]
    }
    st.table(pd.DataFrame(data_trades))
    st.write("**3 Cycles. 3 Wins. 0 Exceptions.**")

with t2:
    st.markdown("### 📊 Strategy vs Buy & Hold")
    data_math = {
        "Entry Point": ["2015 Bear", "2018 Bear", "2022 Bear"],
        "Strategy": ["$6,817,689", "$119,688", "$6,545"],
        "Buy & Hold": ["$286,920", "$19,429", "$4,121"],
        "Advantage": ["24x", "6x", "1.6x"]
    }
    st.table(pd.DataFrame(data_math))
    st.write("**The strategy beats buy and hold at every entry point.**")

# --- 7. 현재 위치 및 미래 예측 ---
st.divider()
st.markdown("### 🔍 Where We Are Now & 5th Halving")
c_now, c_future = st.columns(2)

with c_now:
    st.warning("#### Status: IN PROGRESS")
    st.write("- 18-Month Sell (Oct 2025): **COMPLETE ✅**")
    st.write("- Cash Phase (Oct 2025 ~ Oct 2026): **IN PROGRESS ⏳**")
    st.write("- Next Buy Zone: **~October 2026 (8 Months Away)**")
    st.write("*\"This is the hardest part. The waiting.\"*")

with c_future:
    st.success("#### 2028 Cycle (Expected)")
    future_data = {
        "Year": ["2026", "2027", "2028", "2029"],
        "Phase": ["Bear Market", "Accumulation", "Halving", "Peak"],
        "Action": ["Preserve Capital", "DCA Playbook", "Hold and Ride", "Time-based Exit"]
    }
    st.table(pd.DataFrame(future_data))
