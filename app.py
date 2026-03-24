import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(page_title="Bitcoin Halving Strategy", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 로드 (yfinance 사용) ---
@st.cache_data(ttl=3600)
def get_crypto_data():
    try:
        # 비트코인 최대 기간 데이터 가져오기
        df = yf.download("BTC-USD", period="max", interval="1d")
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. 반감기 및 전략 날짜 설정 ---
HALVINGS = [
    datetime(2012, 11, 28),
    datetime(2016, 7, 9),
    datetime(2020, 5, 11),
    datetime(2024, 4, 20)
]

# --- 4. 메인 대시보드 로직 ---
st.title("₿ Bitcoin Halving 'The Formula' Dashboard")
df_hist = get_crypto_data()

if not df_hist.empty:
    # 차트 생성
    fig = go.Figure()

    # 비트코인 가격 선 (로그 스케일 적용 필수)
    fig.add_trace(go.Scatter(
        x=df_hist['date'], 
        y=df_hist['close'], 
        name="BTC Price", 
        line=dict(color='#f39c12', width=2)
    ))

    # 각 반감기별 수직선 및 구간 표시
    for i, h in enumerate(HALVINGS):
        # A. 반감기 본 날짜 (White)
        fig.add_vline(x=h, line_width=1, line_dash="solid", line_color="rgba(255,255,255,0.5)")
        
        # B. 매도 타점: H + 18개월 (Red)
        sell_date = h + relativedelta(months=18)
        if sell_date < df_hist['date'].max() + relativedelta(months=6):
            fig.add_vline(x=sell_date, line_width=2, line_dash="dash", line_color="#e74c3c")
            fig.add_annotation(x=sell_date, y=0.95, text=f"SELL (H18)", yref="paper", showarrow=False, font=dict(color="#e74c3c"))

        # C. 매수 타점: H + 30개월 (Green)
        buy_date = h + relativedelta(months=30)
        if buy_date < df_hist['date'].max() + relativedelta(months=12):
            fig.add_vline(x=buy_date, line_width=2, line_dash="dash", line_color="#2ecc71")
            fig.add_annotation(x=buy_date, y=0.05, text=f"BUY (H30)", yref="paper", showarrow=False, font=dict(color="#2ecc71"))

    # 차트 레이아웃 설정
    fig.update_layout(
        title="BTC Price History with Halving Strategy Lines",
        yaxis_type="log", # 로그 스케일
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 하단 안내 문구
    st.markdown("""
    - **흰색 실선**: 비트코인 반감기($H$) 발생일
    * **빨간 점선 ($H+18$)**: 역사적 가격 정점 구간 (분할 매도 권장)
    * **초록 점선 ($H+30$)**: 역사적 가격 저점 구간 (분할 매수 권장)
    """)
else:
    st.error("데이터를 불러올 수 없습니다. 잠시 후 새로고침 해주세요.")
