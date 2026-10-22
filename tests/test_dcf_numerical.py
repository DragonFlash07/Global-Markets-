"""Independent synthetic fixtures; no forecasts, providers or book data."""
from dataclasses import replace
from fractions import Fraction

import pandas as pd
import pytest

from core.financial_model import Base, dcf


def test_hand_calculated_two_year_dcf_and_claims():
    # 100/1.1 + 110/1.1^2 = 2000/11; TV=110/.1=1100,
    # PV(TV)=10000/11. EV=12000/11. Bridge=90-200-30-40+20=-160.
    result = dcf(pd.DataFrame({'FCFF': [100, 110]}), Base(), .1, 0,
                 minority_interest=30, preferred_equity=40, nonoperating_assets=20)
    assert result['PV forecast FCFF'] == pytest.approx(float(Fraction(2000, 11)))
    assert result['PV terminal value'] == pytest.approx(float(Fraction(10000, 11)))
    assert result['Enterprise value'] == pytest.approx(float(Fraction(12000, 11)))
    assert result['Equity value'] == pytest.approx(float(Fraction(10240, 11)))
    assert result['Implied price / share'] == pytest.approx(float(Fraction(512, 55)))
    assert result['Terminal value share %'] == pytest.approx(250 / 3)


def test_growing_perpetuity_with_negative_first_year():
    # One explicit outflow of 10; TV=-10*1.02/(.12-.02)=-102.
    result = dcf(pd.DataFrame({'FCFF': [-10]}), Base(), .12, .02)
    assert result['Enterprise value'] == pytest.approx(-100)


def test_default_bridge_and_scale_invariance():
    flows = pd.DataFrame({'FCFF': [100., 110.]})
    value = dcf(flows, Base(), .1, 0)
    assert value['Equity value'] == pytest.approx(float(Fraction(10790, 11)))
    scaled = dcf(flows * 1000, replace(Base(), cash=90000, debt=200000,
                                    shares_millions=100000), .1, 0)
    assert scaled['Implied price / share'] == pytest.approx(value['Implied price / share'])


@pytest.mark.parametrize('flows', [pd.DataFrame(), pd.DataFrame({'FCFF': []}),
    pd.DataFrame({'FCFF': [float('nan')]}), pd.DataFrame({'FCFF': [float('inf')]}),
    pd.DataFrame({'FCFF': ['missing']}), pd.DataFrame([[1, 2]], columns=['FCFF', 'FCFF'])])
def test_invalid_cashflows(flows):
    with pytest.raises(ValueError):
        dcf(flows, Base(), .1, .02)


@pytest.mark.parametrize('wacc,growth', [(.02, .02), (.01, .02),
    (float('nan'), .02), (.1, float('inf')), (-1, -2), (.1, -1)])
def test_invalid_rates(wacc, growth):
    with pytest.raises(ValueError):
        dcf(pd.DataFrame({'FCFF': [100]}), Base(), wacc, growth)


@pytest.mark.parametrize('field,value', [('shares_millions', 0), ('cash', -1),
    ('debt', float('nan')), ('shares_millions', float('inf'))])
def test_invalid_base(field, value):
    with pytest.raises(ValueError):
        dcf(pd.DataFrame({'FCFF': [100]}), replace(Base(), **{field: value}), .1, .02)


@pytest.mark.parametrize('field', ['minority_interest', 'preferred_equity', 'nonoperating_assets'])
@pytest.mark.parametrize('value', [-1, float('nan'), float('inf')])
def test_invalid_bridge(field, value):
    with pytest.raises(ValueError):
        dcf(pd.DataFrame({'FCFF': [100]}), Base(), .1, .02, **{field: value})
