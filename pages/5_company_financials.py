import pandas as pd
import streamlit as st
from core.company_history import load_company, opening_from_history

st.title('Company financials')
company=st.selectbox('Company',['BHP Group','Reliance Jio Infocomm'],key='history_company')
p=load_company(company);k=p['multiplier']
st.subheader(company)
st.caption(f"{p['scope']} · fiscal year end month {p['fiscal_month']} · displayed in {p['currency']} millions · annual snapshots FY2024–FY2026")
st.info('Reported history is separate from analyst forecasts. This snapshot is not refreshed automatically and does not include subsequent quarterly results.')
for msg in p['limitations']:st.caption('• '+msg)
rows=sorted(p['records'],key=lambda x:x['year'])
for tab,section in zip(st.tabs(['Income','Balance sheet','Cash flow','Sources & mapping']),['income','balance','cashflow','sources']):
    with tab:
        if section=='sources':
            for r in rows:
                st.markdown(f"**FY{r['year']}** · {r['sections']}")
                st.link_button(f"Open FY{r['year']} source",r['source'])
                if r.get('balance_source') and r['balance_source']!=r['source']:st.link_button('Balance-sheet comparative source',r['balance_source'])
            st.write('Opening-model mapping (millions):')
            st.json(opening_from_history(company).__dict__)
            st.caption('Asset pool combines PP&E, intangibles and development assets. Other assets/liabilities are explicit sums of remaining disclosed categories. Mapping is aggregated; full asset-vintage, spectrum and tax schedules remain necessary.')
        else:
            data={}
            for r in rows:
                if section=='balance':
                    d={**{'Asset: '+a:v*k for a,v in r['assets'].items()},**{'Liability: '+a:v*k for a,v in r['liabilities'].items()},'Total assets':r['total_assets']*k,'Total equity':r['equity']*k}
                else:d={a:(v if a=='Diluted shares' else v*k) if v is not None else None for a,v in r[section].items()}
                data[f"FY{r['year']} actual"]=d
            df=pd.DataFrame(data)
            st.dataframe(df.style.format('{:,.2f}',na_rep='Not mapped'),use_container_width=True)
            st.download_button('Download '+section+' CSV',df.to_csv(),company.replace(' ','_')+'_'+section+'.csv',mime='text/csv')
st.success('Source snapshot checks: asset totals, assets = liabilities + equity, and CFO + CFI + CFF = net cash movement reconcile.')
st.page_link('pages/3_financial_model.py',label='Build a forecast from reported balances →')
