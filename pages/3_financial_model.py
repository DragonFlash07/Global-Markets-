"""Company-scoped annual modelling workspace."""
from dataclasses import asdict
import hashlib
import json
import pandas as pd
import streamlit as st
from core.research_model import Opening, Annual, project

st.title('Three-statement modelling')
st.caption('Opening balances → annual operating assumptions → financing → linked statements')
company = st.selectbox('Research company', ['BHP Group', 'Reliance Jio Infocomm'], key='research_company')
mode = st.radio('Data basis', ['Company research — enter sourced inputs', 'Learning example — synthetic inputs'], key='model_basis')
learning = mode.startswith('Learning')
source = st.text_input('Opening financials source URL / filing reference', key=f'source_{company}')
period = st.number_input('Opening fiscal year', value=2025, min_value=2000, max_value=2100, key=f'fy_{company}')
currency = st.selectbox('Reporting currency (all amounts and shares in millions)', ['USD','INR','AUD'], index=1 if company.startswith('Reliance') else 0, key=f'currency_{company}')
st.info('BHP: use commodity volume, price and cost evidence to set annual revenue/cost assumptions. Jio: use subscribers, ARPU, network CapEx and spectrum obligations. Segment-driven schedules are not yet implemented.')
if learning:
    st.warning('Synthetic teaching example. These figures do not represent BHP or Jio.')
else:
    st.caption('Enter consolidated/standalone scope consistently. No stock ticker is substituted for Jio. Other assets/liabilities must be sourced, not a balancing plug.')
    st.link_button('Official financial reports', 'https://www.jio.com/about/investor-relations/financials/' if company.startswith('Reliance') else 'https://www.bhp.com/annualreport')
example = Opening(1000,90,120,90,550,0,80,200,0,570,100)
with st.expander('Opening statements · explicit balances', expanded=True):
    inputs = {}
    cols = st.columns(3)
    for i,(key,val) in enumerate(asdict(example).items()):
        with cols[i%3]:
            inputs[key] = st.number_input(key.replace('_',' ').title(), value=float(val) if learning else 0., key=f'opening_{company}_{learning}_{key}')
    st.caption('Shares are diluted shares of this legal entity, not its parent. Other balance-sheet categories are held constant in this initial engine.')
scenario = st.selectbox('Scenario', ['Base','Bull','Bear'])
seed = pd.DataFrame([asdict(Annual(revenue_growth={'Base':.05,'Bull':.08,'Bear':-.02}[scenario])) for _ in range(5)], index=range(int(period)+1,int(period)+6))
st.subheader('Annual assumptions')
st.caption('Rates are decimals (0.05 = 5%). CapEx, depreciation, financing and dividends are absolute amounts in millions. Facility limit is the total available revolver. Scenarios have separate editable grids; their initial values are illustrative.')
drivers = st.data_editor(seed, key=f'drivers_{company}_{scenario}_{period}_{learning}', use_container_width=True)
ack = learning or st.checkbox('I have checked the opening balances, reporting scope, units and source reference.', key=f'ack_{company}')
# Discard old results before rebuilding to avoid valuing stale/invalid inputs.
st.session_state.pop('valuation_model', None)
if not learning and (not source.strip() or not ack):
    st.info('Add a source reference and verify the opening inputs to build a company forecast.')
    st.stop()
try:
    opening = Opening(**inputs)
    forecast = project(opening, [Annual(**row) for row in drivers.to_dict('records')], int(period)+1)
except (ValueError, TypeError) as exc:
    st.error(str(exc)); st.stop()
st.subheader(f'{company} · {scenario} · {currency} millions')
for tab, rows in zip(st.tabs(['Income statement','Balance sheet','Cash flow','Checks']), [
    ['Revenue','COGS','Operating expenses','EBITDA','D&A','EBIT','Interest','EBT','Cash taxes','Net income'],
    ['Cash','Accounts receivable','Inventory','PP&E','Other assets','Total assets','Accounts payable','Term debt','Revolver','Other liabilities','Equity','Liabilities and equity'],
    ['Cash from operations','Investing cash flow','Financing cash flow','Net cash movement','Change in NWC','Unlevered cash taxes','FCFF'],
    ['Balance check','Cash check','Funding shortfall','Tax losses','Unlevered tax losses']]):
    with tab: st.dataframe(forecast[rows].T.style.format('{:,.2f}'), use_container_width=True)
funded = forecast['Funding shortfall'].max() < 1e-6
if not funded: st.error('Funding shortfall: revise CapEx, dividends or committed financing before valuation.')
else:
    fingerprint = hashlib.sha256(json.dumps({'opening':inputs,'drivers':drivers.to_dict(),'company':company,'currency':currency,'scenario':scenario,'source':source,'period':int(period),'learning':learning},sort_keys=True).encode()).hexdigest()[:12]
    st.session_state['valuation_model'] = dict(forecast=forecast,base=opening,company=company,currency=currency,scenario=scenario,source=source,learning=learning,version=fingerprint,period=int(period))
    st.success('Opening and forecast balances reconcile; forecast cash movements are linked.')
    st.page_link('pages/4_dcf_valuation.py',label='Open DCF valuation →')
st.download_button('Export forecast CSV', forecast.to_csv(), 'forecast.csv', mime='text/csv')
st.caption('Initial engine: interest on opening debt; accounting depreciation equals tax depreciation; no deferred taxes, leases, disposals, dilution or changing other balances. Tax losses are carried forward without expiry; local restrictions require separate modelling. Company entry is manually sourced, not audited automatically.')
