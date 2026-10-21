import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.markets import MARKETS
from core.data import candles
from core.indicators import indicators

market = MARKETS[st.session_state['market']]
st.title('📉 Candlestick & technical analysis')
st.caption('Interactive OHLCV charts, SMA, EMA, Bollinger Bands, RSI, MACD and intraday VWAP')
c1,c2,c3,c4 = st.columns([2,1,1,1])
with c1:
    stock = st.selectbox('Example instrument', market['symbols'],
                         index=market['symbols'].index(market['default']))
    symbol = st.text_input('Custom Yahoo ticker (optional)', placeholder='e.g. MSFT or BHP.AX').strip().upper() or stock
with c2:
    interval = st.selectbox('Candle interval', ['1d','1wk','1h','15m','5m'])
with c3:
    options = ['5d','1mo','3mo','6mo','1y','2y','5y'] if interval in ('1d','1wk') else (['5d','1mo'] if interval in ('5m','15m') else ['5d','1mo','3mo','6mo','1y'])
    period = st.selectbox('Period', options, index=min(2, len(options)-1))
with c4:
    overlays = st.multiselect('Overlays', ['SMA20','SMA50','EMA12','EMA26','Bollinger Bands','VWAP'],
                               default=['SMA20','SMA50'])
with st.spinner('Loading OHLCV...'):
    h = candles(symbol, period, interval)
if h.empty or len(h) < 2:
    st.warning('No chart data was returned for this symbol, interval and period. Try a shorter range.')
else:
    h = indicators(h)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=.025,
                        row_heights=[.52,.15,.17,.16])
    fig.add_trace(go.Candlestick(x=h.index, open=h['Open'], high=h['High'], low=h['Low'],
                                 close=h['Close'], name='Candles',
                                 increasing_line_color='#12cc9e', decreasing_line_color='#fa6179'), row=1,col=1)
    colors = ['#12cc9e' if c >= o else '#fa6179' for o,c in zip(h['Open'],h['Close'])]
    for name,color in [('SMA20','#ffbc5c'),('SMA50','#49bfff'),('EMA12','#d09bff'),('EMA26','#e3d77b')]:
        if name in overlays:
            fig.add_trace(go.Scatter(x=h.index,y=h[name],name=name,line=dict(color=color,width=1.5)),row=1,col=1)
    if 'Bollinger Bands' in overlays:
        for name in ['BB upper','BB lower']:
            fig.add_trace(go.Scatter(x=h.index,y=h[name],name=name,line=dict(color='#879bb8',width=1,dash='dot')),row=1,col=1)
    if 'VWAP' in overlays and interval in ('5m','15m','1h') and 'VWAP' in h:
        fig.add_trace(go.Scatter(x=h.index,y=h['VWAP'],name='VWAP',line=dict(color='#ffffff',width=1)),row=1,col=1)
    if 'Volume' in h:
        fig.add_trace(go.Bar(x=h.index,y=h['Volume'],name='Volume',marker_color=colors),row=2,col=1)
    fig.add_trace(go.Scatter(x=h.index,y=h['RSI'],name='RSI (14)',line=dict(color='#ab95ff')),row=3,col=1)
    fig.add_hline(y=70,row=3,col=1,line_dash='dash',line_color='#fa6179')
    fig.add_hline(y=30,row=3,col=1,line_dash='dash',line_color='#12cc9e')
    fig.add_trace(go.Bar(x=h.index,y=h['MACD hist'],name='MACD hist',marker_color=colors),row=4,col=1)
    fig.add_trace(go.Scatter(x=h.index,y=h['MACD'],name='MACD',line=dict(color='#49bfff')),row=4,col=1)
    fig.add_trace(go.Scatter(x=h.index,y=h['MACD signal'],name='Signal',line=dict(color='#ffbc5c')),row=4,col=1)
    fig.update_layout(template='plotly_dark',height=920,hovermode='x unified',
                      xaxis_rangeslider_visible=False,margin=dict(l=20,r=20,t=45,b=20),
                      legend=dict(orientation='h',y=1.04))
    fig.update_yaxes(title_text='Price',row=1,col=1)
    fig.update_yaxes(title_text='Volume',row=2,col=1)
    fig.update_yaxes(title_text='RSI',row=3,col=1)
    fig.update_yaxes(title_text='MACD',row=4,col=1)
    st.plotly_chart(fig,use_container_width=True)
    l,r = st.columns(2)
    l.metric(f'{symbol} · last bar close',f"{h['Close'].iloc[-1]:,.2f}")
    r.metric('Return over selected bars',f"{100*(h['Close'].iloc[-1]/h['Close'].iloc[0]-1):+.2f}%")
    st.caption(f'Last chart bar: {h.index[-1]} · Source: Yahoo/yfinance; not necessarily live.')
    st.download_button('Download OHLCV + indicators',h.to_csv().encode('utf-8'),
                       file_name=f'{symbol.replace("=", "_")}_indicators.csv',mime='text/csv')
