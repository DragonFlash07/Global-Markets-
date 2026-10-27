import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from core.financial_model import Base, Drivers, forecast, dcf
from core.data import statements
from core.markets import MARKETS

st.title('📘 Three-statement model')
st.caption('FMVA-style: forecast drivers → income statement → balance sheet → cash flow → free cash flow')
st.warning('This is an educational, editable forecast, NOT a validated model of a listed company. All default inputs are illustrative and monetary amounts / shares are in MILLIONS of one chosen currency.')
if st.session_state['market'].startswith('Gold'):
    st.info('Spot gold and gold futures do not have corporate financial statements. Use this model for an operating company such as a gold miner; inputs here are a hypothetical company.')

with st.expander('Step 1 · Historical statements from Yahoo (reference only)',expanded=False):
    market = MARKETS[st.session_state['market']]
    default_symbol = market['default'] if market['default'] != 'GC=F' else 'NEM'
    ticker = st.text_input('Yahoo ticker to retrieve company statements',value=default_symbol).upper().strip()
    if st.button('Fetch historical statements'):
        income, balance, cashflow = statements(ticker)
        tabs = st.tabs(['Income','Balance sheet','Cash flow'])
        for tab, data in zip(tabs,[income,balance,cashflow]):
            with tab:
                if data is None or data.empty:
                    st.info('Unavailable for this ticker; try another provider or company filing.')
                else:
                    st.dataframe(data,use_container_width=True)
        st.caption('Fetched values are separate from the editable model; mapping/normalisation and statement audits must be completed before using live company assumptions.')

st.subheader('Step 2 · Opening balance sheet and forecast assumptions')
with st.expander('Opening figures (millions of currency units; FY0)',expanded=False):
    cols = st.columns(3)
    specs = [('revenue','Opening revenue',1000.),('cash','Cash',90.),('receivables','Receivables',120.),
             ('inventory','Inventory',90.),('ppe','Net PP&E',550.),('payables','Payables',80.),
             ('debt','Total debt',200.),('equity','Book equity',570.),('shares_millions','Shares outstanding (millions)',100.)]
    base_inputs = {}
    for i,(key,label,default) in enumerate(specs):
        with cols[i%3]: base_inputs[key] = st.number_input(label,value=default,step=10.,key='b_'+key)

a,b,c,d = st.columns(4)
with a:
    sales_growth = st.slider('Annual revenue growth %',-30,40,8)/100
    cogs = st.slider('COGS / revenue %',0,95,60)/100
    opex = st.slider('Operating expenses / revenue %',0,90,22)/100
with b:
    da = st.slider('D&A / revenue %',0,30,3)/100
    capex = st.slider('CapEx / revenue %',0,40,7)/100
    tax = st.slider('Tax rate %',0,50,25)/100
with c:
    dso = st.slider('Receivables days (DSO)',0,180,44)
    dio = st.slider('Inventory days (DIO)',0,180,55)
    dpo = st.slider('Payables days (DPO)',0,180,49)
with d:
    interest = st.slider('Debt interest %',0,25,6)/100
    payout = st.slider('Dividend payout %',0,100,20)/100
    repayment = st.slider('Annual debt repayment %',0,100,5)/100

try:
    base = Base(**base_inputs)
    assumptions = Drivers(sales_growth, cogs, opex, da, capex, dso, dio, dpo,
                          interest, tax, payout, repayment)
    f = forecast(base, assumptions)
    st.session_state['valuation_model'] = {'forecast': f, 'base': base}
    st.session_state.pop('valuation_model_error', None)
except ValueError as exc:
    st.session_state.pop('valuation_model', None)
    st.session_state['valuation_model_error'] = str(exc)
    st.error(str(exc))
    st.stop()

st.subheader('Step 3 · Linked 5-year financial statements')
inc = ['Revenue','COGS','Operating expenses','D&A','EBIT','Interest','EBT','Taxes','Net income']
bs = ['Cash','Accounts receivable','Inventory','PP&E','Other net assets / (liabilities)',
      'Total assets (net)','Accounts payable','Debt','Equity','Liabilities and equity','Balance check']
cf = ['Cash from operations','Capital expenditure','Investing cash flow','Financing cash flow','Net cash movement','Change in NWC','FCFF']
for tab,rows in zip(st.tabs(['Income statement','Balance sheet','Cash flow / FCFF']),[inc,bs,cf]):
    with tab: st.dataframe(f[rows].T.style.format('{:,.2f}'),use_container_width=True)
check = f['Balance check'].abs().max()
st.success(f'Projected balance-sheet reconciliation · max imbalance: {check:,.8f} million') if check < 1e-6 else st.error(f'Balance mismatch: {check:,.2f} million')
opening_other = base.payables + base.debt + base.equity - (base.cash + base.receivables + base.inventory + base.ppe)
st.caption(f'FY0 balancing residual (Other net assets / liabilities): {opening_other:,.2f} million. Enter real audited opening figures before professional use. Negative forecast cash is possible and signals missing financing, not a valid funding plan.')

st.page_link('pages/4_dcf_valuation.py', label='Continue to DCF valuation →', icon='💎')
st.download_button('Download linked 3-statement forecast CSV',f.to_csv().encode('utf-8'),
                   'financial_model_forecast.csv',mime='text/csv')
st.caption('Simplifications: fixed operating ratios; no deferred tax, lease accounting, SBC, NOLs, M&A or revolving-credit facility; no mid-year convention. Validate inputs and filings independently.')
