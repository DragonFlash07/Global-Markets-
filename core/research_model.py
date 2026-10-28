"""Explicit opening balances, annual schedules and unlevered valuation.
All monetary amounts and shares use millions in one reporting currency.
Opening-debt interest avoids hidden iterative/circular calculation.
"""
from dataclasses import dataclass, asdict
from math import isfinite
from datetime import date
import pandas as pd


@dataclass(frozen=True)
class Opening:
    revenue: float
    cash: float
    receivables: float
    inventory: float
    ppe: float
    other_assets: float
    payables: float
    debt: float
    other_liabilities: float
    equity: float
    shares: float
    tax_losses: float = 0

    def validate(self):
        if not all(isfinite(v) for v in asdict(self).values()):
            raise ValueError('Opening inputs must be finite numbers.')
        if self.revenue <= 0 or self.shares <= 0:
            raise ValueError('Revenue and diluted shares must be positive.')
        if any(v < 0 for k, v in asdict(self).items() if k != 'equity'):
            raise ValueError('Opening assets, liabilities and tax losses cannot be negative.')
        assets = self.cash + self.receivables + self.inventory + self.ppe + self.other_assets
        claims = self.payables + self.debt + self.other_liabilities + self.equity
        if abs(assets - claims) > 1e-6 * max(1, abs(assets)):
            raise ValueError(f'Opening balance sheet does not reconcile: {assets - claims:,.4f} million. No balancing plug is added.')


@dataclass(frozen=True)
class Annual:
    revenue_growth: float = .05
    cogs_ratio: float = .60
    opex_ratio: float = .20
    depreciation: float = 30
    capex: float = 50
    dso: float = 45
    dio: float = 30
    dpo: float = 40
    debt_rate: float = .06
    tax_rate: float = .30
    debt_change: float = 0
    equity_issued: float = 0
    dividends: float = 0
    minimum_cash: float = 0
    facility_limit: float = 0

    def validate(self):
        if not all(isfinite(v) for v in asdict(self).values()):
            raise ValueError('Annual assumptions must be finite numbers.')
        if self.revenue_growth <= -1:
            raise ValueError('Revenue growth must exceed -100%.')
        for key in ('cogs_ratio', 'opex_ratio', 'debt_rate', 'tax_rate'):
            if not 0 <= getattr(self, key) <= 1:
                raise ValueError(f'{key} must be between 0 and 1.')
        if any(getattr(self, key) < 0 for key in ('depreciation','capex','dso','dio','dpo','equity_issued','dividends','minimum_cash','facility_limit')):
            raise ValueError('Schedule amounts/days cannot be negative, except net debt change.')


def project(b: Opening, assumptions: list[Annual], first_year: int) -> pd.DataFrame:
    b.validate()
    if not assumptions:
        raise ValueError('At least one forecast year is required.')
    cash, ar, inv, ap, ppe, debt, eq = b.cash, b.receivables, b.inventory, b.payables, b.ppe, b.debt, b.equity
    revolver, rev, losses, unlevered_losses = 0., b.revenue, b.tax_losses, b.tax_losses
    records = []
    for year, a in enumerate(assumptions, first_year):
        a.validate()
        old_cash, old_rev, old_debt = cash, revolver, debt
        old_nwc = ar + inv - ap
        rev *= 1 + a.revenue_growth
        cogs, opex = rev*a.cogs_ratio, rev*a.opex_ratio
        if a.depreciation > ppe + a.capex:
            raise ValueError(f'{year}: depreciation exceeds available PP&E.')
        ebitda = rev - cogs - opex
        ebit = ebitda - a.depreciation
        interest = (debt + revolver) * a.debt_rate
        ebt = ebit - interest
        used = min(losses, max(ebt, 0))
        tax = max(ebt - used, 0) * a.tax_rate
        losses = losses - used + max(-ebt, 0)
        u_used = min(unlevered_losses, max(ebit, 0))
        u_tax = max(ebit - u_used, 0) * a.tax_rate
        unlevered_losses = unlevered_losses - u_used + max(-ebit, 0)
        ar, inv, ap = rev*a.dso/365, cogs*a.dio/365, cogs*a.dpo/365
        change_nwc = ar + inv - ap - old_nwc
        ni = ebt - tax
        cfo = ni + a.depreciation - change_nwc
        debt += a.debt_change
        if debt < 0:
            raise ValueError(f'{year}: scheduled repayments exceed term debt.')
        available = cash + cfo - a.capex + a.debt_change + a.equity_issued - a.dividends
        draw = min(max(a.minimum_cash - available, 0), max(a.facility_limit - revolver, 0))
        repay = min(max(available - a.minimum_cash, 0), revolver)
        revolver += draw - repay
        if revolver > a.facility_limit + 1e-8:
            raise ValueError(f'{year}: opening revolver exceeds the facility limit.')
        cash = available + draw - repay
        shortfall = max(a.minimum_cash - cash, 0)
        eq += ni + a.equity_issued - a.dividends
        ppe += a.capex - a.depreciation
        assets = cash + ar + inv + ppe + b.other_assets
        claims = ap + debt + revolver + b.other_liabilities + eq
        cff = a.debt_change + draw - repay + a.equity_issued - a.dividends
        records.append({'Year': year, 'Revenue': rev, 'COGS': cogs, 'Operating expenses': opex,
            'EBITDA': ebitda, 'D&A': a.depreciation, 'EBIT': ebit, 'Interest': interest,
            'EBT': ebt, 'Cash taxes': tax, 'Net income': ni, 'Cash': cash,
            'Accounts receivable': ar, 'Inventory': inv, 'PP&E': ppe, 'Other assets': b.other_assets,
            'Total assets': assets, 'Accounts payable': ap, 'Term debt': debt,
            'Revolver': revolver, 'Other liabilities': b.other_liabilities, 'Equity': eq,
            'Liabilities and equity': claims, 'Balance check': assets-claims,
            'Cash from operations': cfo, 'Capital expenditure': a.capex,
            'Investing cash flow': -a.capex, 'Financing cash flow': cff,
            'Net cash movement': cash-old_cash, 'Cash check': cash-old_cash-cfo+a.capex-cff,
            'Change in NWC': change_nwc, 'Tax losses': losses, 'Unlevered tax losses': unlevered_losses,
            'Unlevered cash taxes': u_tax, 'FCFF': ebit-u_tax+a.depreciation-a.capex-change_nwc,
            'Facility movement': revolver-old_rev, 'Funding shortfall': shortfall})
    return pd.DataFrame(records).set_index('Year')


def cost_of_capital(risk_free, beta, premium, debt_cost, tax, equity_weight):
    vals = [risk_free,beta,premium,debt_cost,tax,equity_weight]
    if not all(isfinite(x) for x in vals) or not 0 <= equity_weight <= 1 or not 0 <= tax <= 1 or beta < 0 or min(risk_free,premium,debt_cost) < 0:
        raise ValueError('Invalid WACC inputs or market-value financing weights.')
    re = risk_free + beta*premium
    return re, equity_weight*re+(1-equity_weight)*debt_cost*(1-tax)


def value_business(cashflows, wacc, *, growth=.02, terminal_fcff=None, exit_ebitda=None,
                   exit_multiple=None, cash=0., debt=0., minority=0., preferred=0.,
                   other_assets=0., shares=1., dates=None, valuation_date=None):
    flows = list(cashflows)
    vals = flows+[wacc,growth,cash,debt,minority,preferred,other_assets,shares]
    if not flows or not all(isfinite(x) for x in vals) or wacc <= -1 or shares <= 0:
        raise ValueError('Finite cash flows, valid WACC and positive shares are required.')
    if min(cash,debt,minority,preferred,other_assets) < 0:
        raise ValueError('Enter bridge amounts as positive values.')
    if dates is None:
        times = list(range(1, len(flows)+1))
    else:
        if valuation_date is None or len(dates) != len(flows) or dates != sorted(set(dates)) or any(d <= valuation_date for d in dates):
            raise ValueError('Cash-flow dates must be unique, increasing and after valuation date.')
        times = [(d-valuation_date).days/365 for d in dates]
    if exit_multiple is not None:
        if exit_ebitda is None or not isfinite(exit_multiple) or not isfinite(exit_ebitda) or min(exit_multiple,exit_ebitda) <= 0:
            raise ValueError('Exit multiple and terminal EBITDA must be positive.')
        terminal = exit_ebitda*exit_multiple
    else:
        if growth <= -1 or wacc <= growth:
            raise ValueError('WACC must exceed growth, and growth must exceed -100%.')
        next_cf = flows[-1]*(1+growth) if terminal_fcff is None else terminal_fcff
        if not isfinite(next_cf) or next_cf <= 0:
            raise ValueError('Use a positive normalized next-year terminal FCFF.')
        terminal = next_cf/(wacc-growth)
    pv = sum(cf/(1+wacc)**t for cf,t in zip(flows,times))
    pv_tv = terminal/(1+wacc)**times[-1]
    ev = pv+pv_tv
    eq = ev+cash-debt-minority-preferred+other_assets
    return {'PV forecast FCFF':pv, 'PV terminal value':pv_tv,'Enterprise value':ev,
            'Cash':cash,'Debt':debt,'Minority interest':minority,'Preferred equity':preferred,
            'Other non-operating assets':other_assets,'Equity value':eq,
            'Implied price / share':eq/shares,'Terminal value share %':100*pv_tv/ev if ev else float('nan')}
