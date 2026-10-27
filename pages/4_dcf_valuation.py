"""Valuation workspace using the latest explicit forecast in this session."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from core.financial_model import dcf

st.title('💎 DCF valuation')
st.caption('Linked forecast → discounted FCFF → enterprise value → equity value')
model = st.session_state.get('valuation_model')
if model is None:
    st.info('Build a three-statement forecast first. Its inputs and cash flows will be carried into this page for this session.')
    st.page_link('pages/3_financial_model.py', label='Build financial forecast', icon='📘')
    st.stop()
f, base = model['forecast'], model['base']
st.warning('Illustrative company model. Amounts and shares are in millions of one currency; price per share is in currency units. Historical Yahoo statements are not automatically mapped to these inputs.')
st.page_link('pages/3_financial_model.py', label='Review or edit forecast assumptions', icon='📘')
with st.expander('Forecast used in this valuation', expanded=False):
    st.dataframe(f[['Revenue', 'EBIT', 'FCFF']].T, use_container_width=True)
    st.caption(f'Opening cash: {base.cash:,.2f} · debt: {base.debt:,.2f} · shares: {base.shares_millions:,.2f} million')
a, b = st.columns(2)
with a: wacc = st.number_input('WACC %', min_value=1.0, max_value=40.0, value=10.0, step=.5) / 100
with b: growth = st.number_input('Perpetual terminal growth %', min_value=-5.0, max_value=15.0, value=3.0, step=.5) / 100
try:
    value = dcf(f, base, wacc, growth)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
if f['FCFF'].iloc[-1] <= 0:
    st.warning('Terminal FCFF is not positive. A perpetual-growth terminal value may not be economically meaningful.')
st.subheader('Valuation summary')
m = st.columns(4)
for col,key in zip(m,['Enterprise value','Equity value','Implied price / share','Terminal value share %']):
    col.metric(key,f"{value[key]:,.2f}"+(' %' if key.endswith('%') else ''))
fig = go.Figure()
fig.add_bar(x=f.index,y=f['FCFF'],name='Projected FCFF',marker_color='#1dcaa2')
fig.update_layout(title='Projected unlevered free cash flows (millions)',template='plotly_dark',height=330)
st.plotly_chart(fig,use_container_width=True)

st.markdown('#### WACC / perpetual-growth sensitivity · implied price per share')
ws = [wacc + x/100 for x in [-2,-1,0,1,2]]
gs = [growth + x/100 for x in [-1,-.5,0,.5,1]]
rows=[]
for ww in ws:
    rec={'WACC':f'{ww:.1%}'}
    for gg in gs:
        rec[f'{gg:.1%}'] = round(dcf(f,base,ww,gg)['Implied price / share'],2) if ww > gg else None
    rows.append(rec)
st.dataframe(pd.DataFrame(rows).set_index('WACC'),use_container_width=True)

st.caption('Year-end discounting; enterprise value plus opening cash less opening debt. No lease, minority-interest or other non-operating adjustments are included.')
st.download_button('Download valuation CSV', pd.Series(value).to_csv(), 'dcf_valuation.csv', mime='text/csv')
