from dataclasses import replace
from datetime import date
import pytest
from core.research_model import Opening, Annual, project, value_business, cost_of_capital
B=Opening(1000,90,120,90,550,0,80,200,0,570,100)
def test_no_plug():
    with pytest.raises(ValueError,match='does not reconcile'): project(replace(B,equity=571),[Annual()],2026)
def test_financing_and_links():
    f=project(B,[Annual(capex=500,facility_limit=1000),Annual(facility_limit=1000)],2026)
    assert f['Balance check'].abs().max()<1e-8
    assert f['Cash check'].abs().max()<1e-8
    assert f.iloc[0]['Revolver']>f.iloc[1]['Revolver']>0
    assert f.iloc[1]['Interest']==pytest.approx((f.iloc[0]['Term debt']+f.iloc[0]['Revolver'])*.06)
def test_shortfall():
    assert project(B,[Annual(capex=500)],2026).iloc[0]['Funding shortfall']>0
def test_losses():
    f=project(B,[Annual(cogs_ratio=.9,opex_ratio=.3),Annual()],2026)
    assert f.iloc[0]['Unlevered cash taxes']==0
    assert f.iloc[0]['Tax losses']>0
    assert f.iloc[1]['Unlevered cash taxes']<max(f.iloc[1]['EBIT'],0)*.3
def test_exhaustion():
    with pytest.raises(ValueError,match='PP&E'): project(B,[Annual(depreciation=900)],2026)
def test_independent_dcf():
    v=value_business([100,110],.1,growth=0,cash=90,debt=200,minority=30,preferred=40,other_assets=20,shares=100)
    assert v['Enterprise value']==pytest.approx(12000/11)
    assert v['Implied price / share']==pytest.approx(512/55)
def test_wacc():
    re,w=cost_of_capital(.04,1.2,.05,.06,.3,.8)
    assert re==pytest.approx(.1)
    assert w==pytest.approx(.0884)
def test_timing_and_exit():
    assert value_business([100],.1,exit_ebitda=200,exit_multiple=5)['Enterprise value']==pytest.approx(1000)
    assert value_business([100],.1,growth=0,dates=[date(2025,1,1)],valuation_date=date(2024,1,2))['Enterprise value']==pytest.approx(1000)
@pytest.mark.parametrize('flows,w,g,shares',[([],.1,.02,1),([float('nan')],.1,.02,1),([1],.02,.03,1),([1],.1,.02,0)])
def test_invalid(flows,w,g,shares):
    with pytest.raises(ValueError): value_business(flows,w,growth=g,shares=shares)
