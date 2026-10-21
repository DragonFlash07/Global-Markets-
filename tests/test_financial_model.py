import math
import pytest
from core.financial_model import Base, Drivers, forecast, dcf
from core.data import build_mover_table
import pandas as pd


def test_balance_and_cashflow_link():
    b, a = Base(), Drivers()
    f = forecast(b, a)
    assert (f['Balance check'].abs() < 1e-7).all()
    assert (f['Cash from operations'] + f['Investing cash flow'] + f['Financing cash flow'] - f['Net cash movement']).abs().max() < 1e-7
    assert f.loc['Y1','Cash'] == pytest.approx(b.cash+f.loc['Y1','Net cash movement'])


def test_dcf_identity_and_monotonicity():
    b,a=Base(),Drivers()
    f=forecast(b,a)
    low=dcf(f,b,.09,.03)
    high=dcf(f,b,.11,.03)
    assert low['Implied price / share'] > high['Implied price / share']
    assert low['Equity value'] == pytest.approx(low['Enterprise value'] + b.cash - b.debt)


def test_invalid_terminal_growth():
    with pytest.raises(ValueError):
        forecast(Base(), Drivers(wacc=.03,terminal_growth=.04))


def test_intraday_uses_previous_session_close():
    dates=pd.to_datetime(['2026-10-19','2026-10-20'])
    day=pd.DataFrame({'A':[100.,105.]},index=dates)
    idx=pd.DatetimeIndex(['2026-10-20T10:00:00+05:30'])
    intra=pd.DataFrame({'A':[108.]},index=idx)
    x=build_mover_table(day,intra,'Asia/Kolkata')
    assert x.iloc[0]['Previous close']==100.
    assert x.iloc[0]['Last']==108.
    assert x.iloc[0]['Change %']==pytest.approx(8.)
