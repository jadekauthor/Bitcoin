import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests

# --- 1. 실시간 시세 가져오기 (CoinGecko) ---
@st.cache_data(ttl=60)
def get_btc_info():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin", "price_change_percentage": "24h"}
    try:
        data = requests.get(url, params=params).json()[0]
        return data
    except:
        return None

# --- 2. 기본 설정 ---
H_DATE = datetime(2024, 4, 20) # 4차 반감기
TODAY = datetime.now()

# 페이지 설정
st.set_page_config(page_title="BTC Cycle Master", layout="wide")
st.title("🧡 Bitcoin Halving Formula App")

# --- 3. 상단 대시보드 (시세) ---
info = get_btc_info()
if info:
    c1, c2, c3 = st.columns(3)
    c1.metric("현재가 (USD)", f"${info['current_price']:,.0f}", f"{info['price_change_percentage_24h']:.2f}%")
    c2.metric("24h 거래량", f"${info['total_volume']:,.0f}")
    c3.metric("시가총액 순위", f"Rank #{info['market_cap_rank']}")

st.divider()

# --- 4. 공식 로직 계산 ---
diff = relativedelta(TODAY, H_DATE)
months_passed = diff.years * 12 + diff.months

# 상태 판별
if months_passed <= 12:
    status, color, msg = "HOLD (관망)", "blue", "현금화 준비 단계입니다."
elif 12 < months_passed <= 18:
    status, color, msg = "CASH PHASE", "orange", "매도 완료 및 현금 보유 구간입니다."
elif 18 < months_passed <= 30:
    status, color, msg = "BUY WINDOW", "green", "매수 타이밍을 노려야 하는 구간입니다."
else:
    status, color, msg = "REPEAT", "red", "새로운 사이클이 시작되었습니다."

# --- 5. 화면 표시 ---
col_l, col_r = st.columns([1, 1])

with col_l:
    st.subheader("🎯 현재 사이클 분석")
    st.info(f"**현재 상태: {status}**")
    st.write(f"반감기 이후 **{months_passed}개월**이 지났습니다.")
    st.success(f"가이드: {msg}")

with col_r:
    st.subheader("📅 역대 반감기 히스토리")
    history = {
        "차수": ["1차", "2차", "3차", "4차(H)"],
        "날짜": ["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20"]
    }
    st.table(pd.DataFrame(history))

st.divider()
st.caption("공식 출처: Bitcoin Jae (@BitcoinxDaily) Strategy")