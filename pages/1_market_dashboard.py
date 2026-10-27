from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import plotly.express as px
from core.data import movers, candles
from core.markets import MARKETS

selected = st.session_state['market']
config = MARKETS[selected]
st.title('GLOBAL MARKET DASHBOARD')
choice = st.radio('Markets', list(MARKETS), index=list(MARKETS).index(selected), horizontal=True, label_visibility='collapsed')
if choice != selected:
    st.session_state['market'] = choice
    st.rerun()
st.header(selected.split(' · ')[0] + ' markets')
st.caption('India · USA · ASX · Gold | five-minute screen updates, subject to market hours and vendor delays')
st.info('Rankings cover ONLY the sample symbols configured for the selected market, not every stock on the exchange. Data rerun ≠ a new exchange quote.')

@st.fragment(run_every='300s')
def refresh_panels():
    now = datetime.now(ZoneInfo(config['timezone']))
    st.caption(f"Last screen refresh: {now:%Y-%m-%d %H:%M:%S %Z} · next attempt in 5 min while page is open")
    if st.button('🔄 Refresh prices now', key='refresh_markets'):
        movers.clear()
        candles.clear()
    if config['indices']:
        quotes = movers(tuple(config['indices'].values()), config['timezone'])
        cards = st.columns(len(config['indices']))
        for col, (label, symbol) in zip(cards, config['indices'].items()):
            row = quotes.loc[quotes['Symbol'] == symbol] if not quotes.empty else quotes
            if row.empty:
                col.metric(label, 'Unavailable')
            else:
                q = row.iloc[0]
                col.metric(label, f"{q['Last']:,.2f}", f"{q['Change %']:+.2f}%")
                col.caption(f"{q['Source']} · {q['As of']}")
    with st.spinner('Loading latest available quotes...'):
        df = movers(tuple(config['symbols']), config['timezone'])
    if df.empty:
        st.warning('No usable quotes returned. Check network / Yahoo response or try again. No figures are fabricated.')
        return
    st.subheader('Top 5 movers in selected universe')
    if selected.startswith('Gold'):
        st.caption('Gold futures and ETFs are different instruments, not an exchange-wide stock ranking; prices may use different currencies.')
    left, right = st.columns(2)
    for col, subset, name in ((left, df[df['Change %'] > 0].nlargest(5, 'Change %'), '🟢 Top gainers'),
                               (right, df[df['Change %'] < 0].nsmallest(5, 'Change %'), '🔴 Top losers')):
        with col:
            st.markdown(f'#### {name}')
            if subset.empty:
                st.caption('No qualifying movers in this snapshot.')
            else:
                chart = px.bar(subset.sort_values('Change %'), x='Change %', y='Symbol', orientation='h', text='Change %')
                chart.update_traces(marker_color='#00c853' if 'gainers' in name else '#ff1744', texttemplate='%{x:+.2f}%', textposition='outside', cliponaxis=False)
                chart.update_layout(template='plotly_dark', height=320, margin=dict(l=0,r=65,t=10,b=10), xaxis_title='Change vs previous close (%)', yaxis_title=None)
                st.plotly_chart(chart, use_container_width=True)
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
