"""Global Market Lab V2: entry point."""
import streamlit as st
from core.markets import MARKETS

st.set_page_config(page_title="Global Market Lab V2", page_icon="🌐", layout="wide")
st.markdown('''<style>
.stApp {background:#0b1220;color:#e7edf5} 
[data-testid="stMetric"] {background:#142035;padding:16px;border:1px solid #273953;border-radius:12px}
[data-testid="stSidebar"] {background:#101b2d}
h1,h2,h3{letter-spacing:-.03em}
</style>''', unsafe_allow_html=True)
with st.sidebar:
    st.markdown('## 🌐 GLOBAL MARKET LAB')
    market = st.selectbox('Market', list(MARKETS), key='market')
    st.caption('Educational research terminal · prototype V2')
    st.divider()
    st.caption('Yahoo/yfinance is unofficial and may be delayed or incomplete. Not for trading or commercial redistribution. All times/data are source dependent.')

st.navigation([
    st.Page('pages/1_market_dashboard.py', title='Market dashboard', icon='🌍', default=True),
    st.Page('pages/2_candlestick_lab.py', title='Technical chart lab', icon='📉'),
    st.Page('pages/3_financial_model.py', title='Three-statement model', icon='📘'),
    st.Page('pages/4_dcf_valuation.py', title='DCF valuation', icon='💎'),
]).run()
