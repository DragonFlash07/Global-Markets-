"""Source-labelled annual snapshots. No network or fabricated fallback values."""
import json
from pathlib import Path
from .research_model import Opening, Annual


def load_company(company):
    with (Path(__file__).resolve().parents[1]/'data/company_history.json').open() as f:
        pack=json.load(f)[company]
    for r in pack['records']:
        for actual,expected,label in [(sum(r['assets'].values()),r['total_assets'],'assets'),(sum(r['liabilities'].values())+r['equity'],r['total_assets'],'balance'),(r['cashflow']['CFO']+r['cashflow']['CFI']+r['cashflow']['CFF'],r['cashflow']['Net cash movement'],'cash movement')]:
            if abs(actual-expected)>.1:raise ValueError(f"{company} FY{r['year']}: {label} failed reconciliation")
    return pack


def opening_from_history(company):
    p=load_company(company);r=max(p['records'],key=lambda x:x['year']);a=r['assets'];l=r['liabilities'];k=p['multiplier']
    # Explicit grouping of disclosed components, not total-minus-known balancing plugs.
    if company=='BHP Group':
        used=['cash','receivables_current','inventory_current','inventory_noncurrent','ppe','intangibles']
        used_l=['payables_current','payables_noncurrent','borrowings_current','borrowings_noncurrent']
        inv=a['inventory_current']+a['inventory_noncurrent'];pay=l['payables_current']+l['payables_noncurrent']
        assets=a['ppe']+a['intangibles']
        debt=l['borrowings_current']+l['borrowings_noncurrent']
    else:
        used=['cash','receivables_current','ppe','spectrum','intangibles','construction','spectrum_development','intangible_development']
        used_l=['payables_small','payables_other','borrowings_current','borrowings_noncurrent','leases_current','leases_noncurrent','spectrum_debt_current','spectrum_debt_noncurrent']
        inv=0;pay=l['payables_small']+l['payables_other']
        assets=sum(a[x] for x in ['ppe','spectrum','intangibles','construction','spectrum_development','intangible_development'])
        debt=sum(l[x] for x in used_l if not x.startswith('payables'))
    b=Opening(revenue=r['income']['Revenue']*k,cash=a['cash']*k,receivables=a['receivables_current']*k,inventory=inv*k,ppe=assets*k,other_assets=sum(v for key,v in a.items() if key not in used)*k,payables=pay*k,debt=debt*k,other_liabilities=sum(v for key,v in l.items() if key not in used_l)*k,equity=r['equity']*k,shares=r['income']['Diluted shares'])
    b.validate()
    return b


def annual_baseline(company):
    p=load_company(company);r=max(p['records'],key=lambda x:x['year']);i=r['income'];k=p['multiplier'];b=opening_from_history(company)
    costs=(i['Revenue']-i['EBIT']-i['D&A'])/i['Revenue']
    capex=(r['cashflow']['Cash PP&E expenditure']+r['cashflow']['Exploration expenditure']) if company=='BHP Group' else r['cashflow']['Cash asset expenditure']
    # Flat sales and cash cost/tax defaults are editable modelling assumptions, not guidance.
    return Annual(revenue_growth=0,cogs_ratio=costs,opex_ratio=0,depreciation=i['D&A']*k,capex=capex*k,dso=b.receivables/b.revenue*365,dio=b.inventory/(costs*b.revenue)*365,dpo=b.payables/(costs*b.revenue)*365,debt_rate=.06,tax_rate=.30 if company=='BHP Group' else .2517)
