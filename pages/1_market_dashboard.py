from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import plotly.express as px
from core.data import movers, candles
from core.markets import MARKETS

selected = st.session_state['market']
config = MARKETS[selected]
st.title('🌍 Market overview')
st.caption('India · USA · ASX · Gold | five-minute screen updates, subject to market hours and vendor delays')

@st.fragment(run_every='300s')
def refresh_panels():
    now = datetime.now(ZoneInfo(config['timezone']))
    st.caption(f"Last screen refresh: {now:%Y-%m-%d %H:%M:%S %Z} · next attempt in 5 min while page is open")
    if st.button('🔄 Refresh prices now', key='refresh_markets'):
        movers.clear()
        candles.clear()
    # Separate benchmark request keeps indices out of stock rankings and exports.
    with st.spinner('Loading market summary...'):
        summary = movers(tuple(config['indices'].values()), config['timezone'])
    columns = st.columns(len(config['indices']))
    for col, (label, symbol) in zip(columns, config['indices'].items()):
        with col:
            quote = summary.loc[summary['Symbol'] == symbol] if not summary.empty else summary
            if quote.empty:
                st.metric(label, 'Unavailable', help=f'{symbol} · No usable quote returned by Yahoo.')
            else:
                row = quote.iloc[0]
                st.metric(label, f"{row['Last']:,.2f}", f"{row['Change %']:+.2f}%",
                          help=f"{symbol} · Change versus previous session close: {row['Previous close']:,.2f}")
                st.caption(f"{symbol} · {row['Source']} · {row['As of']}")
    st.caption('Yahoo/yfinance · latest available bars, potentially delayed. Percentage change is versus the previous market-session close. Each instrument has its own quote time.')
    st.divider()
    st.info('Rankings cover ONLY the sample symbols configured for the selected market, not every stock on the exchange. Data rerun ≠ a new exchange quote.')
    with st.spinner('Loading latest available quotes...'):
        df = movers(tuple(config['symbols']), config['timezone'])
    if df.empty:
        st.warning('No usable quotes returned. Check network / Yahoo response or try again. No figures are fabricated.')
        return
    st.subheader('Top 5 movers in selected universe')
    if selected.startswith('Gold'):
        st.caption('Gold futures and ETFs are different instruments, not an exchange-wide stock ranking; prices may use different currencies.')
    left, right = st.columns(2)
    for col, subset, name in ((left, df.nlargest(5, 'Change %'), '🟢 Top gainers'),
                               (right, df.nsmallest(5, 'Change %'), '🔴 Top losers')):
        with col:
            st.markdown(f'#### {name}')
            st.dataframe(subset[['Symbol', 'Last', 'Change %', 'Source', 'As of']].round(2),
                         use_container_width=True, hide_index=True)
    st.subheader('Universe heatmap')
    plot_df = df.copy()
    plot_df['Weight'] = 1
    fig = px.treemap(plot_df, path=['Symbol'], values='Weight', color='Change %',
                     color_continuous_scale=['#e14f69', '#22334a', '#1dcaa2'],
                     color_continuous_midpoint=0,
                     hover_data={'Last':':.2f','As of':True,'Weight':False})
    fig.update_layout(template='plotly_dark', height=440, margin=dict(t=12,l=0,r=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.download_button('Download snapshot CSV', df.to_csv(index=False),
                       file_name='market_snapshot.csv', mime='text/csv')

refresh_panels()
st.caption('Daily/5-minute Yahoo bars have variable exchange delays; not a guaranteed real-time feed. Markets do not move outside sessions.')
