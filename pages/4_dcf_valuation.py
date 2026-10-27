import pandas as pd
import streamlit as st
from core.research_model import cost_of_capital, value_business

st.title('DCF valuation')
model = st.session_state.get('valuation_model')
if not model:
    st.info('Build and reconcile a three-statement forecast first.')
    st.page_link('pages/3_financial_model.py',label='Open three-statement model'); st.stop()
f,b = model['forecast'],model['base']
st.subheader(f"{model['company']} · {model['scenario']} · {model['currency']}")
st.caption(f"Forecast snapshot {model['version']} · opening FY{model['period']} · amounts and shares in millions")
if model['learning']: st.warning('Synthetic learning example — not a company valuation.')
else: st.caption('Source reference: '+model['source'])
st.page_link('pages/3_financial_model.py', label='Edit forecast assumptions')
st.subheader('Cost of capital')
with st.expander('CAPM and market-value financing weights', expanded=True):
    a,c,d = st.columns(3)
    rf=a.number_input('Risk-free rate %', value=4., min_value=0.)/100
    beta=c.number_input('Levered beta',value=1.,min_value=0.)
    erp=d.number_input('Equity risk premium %',value=5.,min_value=0.)/100
    rd=a.number_input('Pre-tax cost of debt %',value=6.,min_value=0.)/100
    tax=c.number_input('Marginal tax rate %',value=30.,min_value=0.,max_value=100.)/100
    ew=d.number_input('Equity market-value weight %',value=80.,min_value=0.,max_value=100.)/100
    re,wacc=cost_of_capital(rf,beta,erp,rd,tax,ew)
    st.caption(f'Cost of equity: {re:.2%} · calculated WACC: {wacc:.2%}. Defaults are illustrative; rates must match the reporting currency.')
    evidence=st.text_input('WACC sources and as-of date')
if not model['learning'] and not evidence.strip():
    st.info('Document the WACC sources and date before computing a company valuation.'); st.stop()
method=st.radio('Terminal method',['Perpetual growth','Exit EBITDA multiple'], horizontal=True)
g=st.number_input('Terminal growth %',value=2.,min_value=-10.,max_value=20.)/100
norm=st.number_input('Normalized next-year terminal FCFF (millions)',value=max(float(f['FCFF'].iloc[-1])*(1+g),0.),min_value=0.)
multiple=st.number_input('Exit EBITDA multiple',value=7.,min_value=.1)
st.caption('Normalize terminal reinvestment and margins explicitly. This control does not automatically validate growth versus reinvestment. Annual year-end discounting is used here; no partial-year adjustment.')
with st.expander('Enterprise-to-equity bridge',expanded=True):
    cols=st.columns(3)
    adjustments={}
    for i,(key,label,default) in enumerate([('cash','Opening cash',b.cash),('debt','Opening debt',b.debt),('minority','Non-controlling interests',0.),('preferred','Preferred equity',0.),('other_assets','Non-operating assets excluding cash',0.),('shares','Diluted shares (millions)',b.shares)]):
        adjustments[key]=cols[i%3].number_input(label,value=float(default),min_value=0.)
    st.caption('Use a valuation-date bridge consistently. Lease/spectrum obligations must be classified once, without double-counting related operating cash flows.')
try:
    kw=dict(growth=g,terminal_fcff=norm,**adjustments)
    if method.startswith('Exit'):kw.update(exit_multiple=multiple,exit_ebitda=float(f['EBITDA'].iloc[-1]))
    result=value_business(f['FCFF'],wacc,**kw)
except ValueError as exc:
    st.error(str(exc));st.stop()
for col,key in zip(st.columns(3),['Enterprise value','Equity value','Implied price / share']):col.metric(key,f'{result[key]:,.2f}')
st.caption(f"Terminal value contribution: {result['Terminal value share %']:.1f}%")
st.bar_chart(f[['FCFF']])
st.dataframe(pd.Series(result,name='Value').to_frame(),use_container_width=True)
if method.startswith('Perpetual'):
    sensitivity={}
    for ww in [wacc-.02,wacc-.01,wacc,wacc+.01,wacc+.02]:
        row={}
        for gg in [g-.01,g-.005,g,g+.005,g+.01]:
            row[f'{gg:.1%}']=value_business(f['FCFF'],ww,**{**kw,'growth':gg,'terminal_fcff':norm*(1+gg)/(1+g)})['Implied price / share'] if ww>gg and ww>-1 else None
        sensitivity[f'{ww:.2%}']=row
    st.subheader('WACC × growth sensitivity · price per share')
    st.dataframe(pd.DataFrame.from_dict(sensitivity,orient='index'),use_container_width=True)
st.download_button('Export valuation CSV',pd.Series(result).to_csv(),'valuation.csv',mime='text/csv')
