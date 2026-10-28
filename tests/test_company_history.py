import pytest
from core.company_history import load_company, opening_from_history, annual_baseline
from core.research_model import project

@pytest.mark.parametrize('company',['BHP Group','Reliance Jio Infocomm'])
def test_all_snapshots(company):
    p=load_company(company)
    assert sorted(r['year'] for r in p['records'])==[2024,2025,2026]
    for r in p['records']:
        assert sum(r['assets'].values())==r['total_assets']
        assert sum(r['liabilities'].values())+r['equity']==r['total_assets']
        cf=r['cashflow']
        if company=='BHP Group':
            assert cf['Opening cash net of overdrafts']+cf['Net cash movement']+cf['FX on cash']==cf['Closing cash net of overdrafts']
        else:assert cf['Opening cash']+cf['Net cash movement']==cf['Closing cash']

def test_jio_scale():
    b=opening_from_history('Reliance Jio Infocomm')
    assert b.cash==92920
    assert b.revenue==1288710
    assert b.debt==(50133+17672+7480+6299+99552+4962)*10
    assert b.shares==pytest.approx(168893.835616)

def test_bhp_scope():
    b=opening_from_history('BHP Group')
    assert b.cash==18532
    assert b.debt==27121
    assert b.equity==56321
    assert b.ppe==80046+2113

@pytest.mark.parametrize('company',['BHP Group','Reliance Jio Infocomm'])
def test_forecast_from_history(company):
    f=project(opening_from_history(company),[annual_baseline(company)]*5,2027)
    assert f['Balance check'].abs().max()<1e-6
    assert f['Cash check'].abs().max()<1e-6
    assert f['Funding shortfall'].max()==0
