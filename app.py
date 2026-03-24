import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Bitcoin Strategy Dashboard", layout="wide")

# --- 2. 데이터 로드 함수 (개선됨) ---
@st.cache_data(ttl=3600)
def get_crypto_data():
    try:
        # 'auto_adjust=True'를 추가하여 안정성을 높임
        df = yf.download("BTC-USD", period="max", interval="1d", auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        # yfinance 버전에 따라 컬럼명이 다를 수 있어 소문자로 통일
        df.columns = [str(c).lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"데이터 엔진 오류: {e}")
        return pd.DataFrame()

# --- 3. 전략 설정 ---
HALVINGS = [datetime(2012,11,28), datetime(2016,7,9), datetime(2020,5,11), datetime(2024,4,20)]
TODAY = datetime.now()

# --- 4. 메인 화면 구성 ---
st.title("₿ Bitcoin Halving 'The Formula'")

df_hist = get_crypto_data()

if not df_hist.empty:
    # 실시간 가격 (데이터프레임의 마지막 값 사용)
    current_price = df_hist['close'].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"${current_price:,.0f}")
    c2.metric("Data Range", f"{df_hist['date'].min().year} - {df_hist['date'].max().year}")
    c3.metric("Next Halving", "~April 2028")

    # 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_hist['date'], y=df_hist['close'], name="BTC", line=dict(color='#f39c12')))

    for h in HALVINGS:
        # 반감기선
        fig.add_vline(x=h, line_width=1, line_dash="solid", line_color="rgba(255,255,255,0.3)")
        # SELL선 (H+18)
        s_date = h + relativedelta(months=18)
        if s_date < df_hist['date'].max() + relativedelta(months=6):
            fig.add_vline(x=s_date, line_width=2, line_dash="dash", line_color="#e74c3c")
        # BUY선 (H+30)
        b_date = h + relativedelta(months=30)
        if b_date < df_hist['date'].max() + relativedelta(months=12):
            fig.add_vline(x=b_date, line_width=2, line_dash="dash", line_color="#2ecc71")

    fig.update_layout(yaxis_type="log", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("⚠️ 현재 Yahoo Finance 서버 연결이 원활하지 않습니다.")
    st.info("해결 방법: 1~2분 후 브라우저를 '새로고침' 하거나, GitHub에서 코드를 다시 한번 Save(Commit) 해주세요.")
