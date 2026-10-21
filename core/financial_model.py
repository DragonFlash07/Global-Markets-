"""Simple linked 3-statement, unlevered DCF model. Monetary inputs are in *millions*."""
from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class Base:
    revenue: float = 1000
    cash: float = 90
    receivables: float = 120
    inventory: float = 90
    ppe: float = 550
    payables: float = 80
    debt: float = 200
    equity: float = 570
    shares_millions: float = 100


@dataclass(frozen=True)
class Drivers:
    sales_growth: float = .08
    cogs_ratio: float = .60
    opex_ratio: float = .22
    depreciation_ratio: float = .03
    capex_ratio: float = .07
    dso: float = 44
    dio: float = 55
    dpo: float = 49
    interest_rate: float = .06
    tax_rate: float = .25
    dividend_payout: float = .20
    debt_repay_ratio: float = .05
    wacc: float = .10
    terminal_growth: float = .03


def forecast(b: Base, a: Drivers, years: int = 5) -> pd.DataFrame:
    if years < 1 or b.shares_millions <= 0 or b.revenue <= 0:
        raise ValueError('Choose positive revenue/shares and at least one forecast year.')
    if any(not 0 <= x <= 1 for x in (a.cogs_ratio, a.opex_ratio, a.depreciation_ratio, a.capex_ratio, a.tax_rate, a.dividend_payout, a.debt_repay_ratio)):
        raise ValueError('Financial ratio inputs must be between 0 and 100%.')
    if a.wacc <= a.terminal_growth:
        raise ValueError('WACC must exceed perpetual terminal growth.')
    if a.sales_growth <= -1:
        raise ValueError('Sales cannot decline by 100% or more each year.')
    if min(b.cash, b.receivables, b.inventory, b.ppe, b.payables, b.debt) < 0:
        raise ValueError('Base statement assets and liabilities cannot be negative.')
    # Transparent FY0 balancing item. Should be replaced by actual historical other assets/net liabilities.
    other_net_assets = b.payables + b.debt + b.equity - (b.cash + b.receivables + b.inventory + b.ppe)
    revenue, cash, ar, inv, ppe, ap, debt, equity = (b.revenue, b.cash, b.receivables,
                                                   b.inventory, b.ppe, b.payables, b.debt, b.equity)
    out = []
    for yr in range(1, years + 1):
        opening_cash, opening_debt = cash, debt
        opening_nwc = ar + inv - ap
        revenue = revenue * (1 + a.sales_growth)
        cogs = revenue * a.cogs_ratio
        opex = revenue * a.opex_ratio
        da = revenue * a.depreciation_ratio
        ebit = revenue - cogs - opex - da
        interest = opening_debt * a.interest_rate
        ebt = ebit - interest
        tax = max(0, ebt) * a.tax_rate  # Simplified; no NOL rollforward.
        net_income = ebt - tax
        ar = revenue * a.dso / 365
        inv = cogs * a.dio / 365
        ap = cogs * a.dpo / 365
        nwc = ar + inv - ap
        delta_nwc = nwc - opening_nwc
        cfo = net_income + da - delta_nwc
        capex = revenue * a.capex_ratio
        debt_repayment = min(opening_debt, opening_debt * a.debt_repay_ratio)
        dividends = max(net_income, 0) * a.dividend_payout
        cfi, cff = -capex, -debt_repayment - dividends
        cash = opening_cash + cfo + cfi + cff
        ppe = ppe + capex - da
        debt = opening_debt - debt_repayment
        equity = equity + net_income - dividends
        assets = cash + ar + inv + ppe + other_net_assets
        liabilities_equity = ap + debt + equity
        fcff = ebit * (1 - a.tax_rate) + da - capex - delta_nwc
        out.append({
            'Year': f'Y{yr}', 'Revenue': revenue, 'COGS': cogs, 'Operating expenses': opex,
            'D&A': da, 'EBIT': ebit, 'Interest': interest, 'EBT': ebt, 'Taxes': tax,
            'Net income': net_income,
            'Cash': cash, 'Accounts receivable': ar, 'Inventory': inv, 'PP&E': ppe,
            'Other net assets / (liabilities)': other_net_assets, 'Total assets (net)': assets,
            'Accounts payable': ap, 'Debt': debt, 'Equity': equity,
            'Liabilities and equity': liabilities_equity, 'Balance check': assets - liabilities_equity,
            'Cash from operations': cfo, 'Capital expenditure': capex,
            'Investing cash flow': cfi, 'Financing cash flow': cff,
            'Net cash movement': cfo + cfi + cff, 'Change in NWC': delta_nwc,
            'FCFF': fcff
        })
    return pd.DataFrame(out).set_index('Year')


def dcf(f: pd.DataFrame, b: Base, wacc: float, terminal_growth: float) -> dict:
    if wacc <= terminal_growth:
        raise ValueError('WACC must exceed terminal growth.')
    if b.shares_millions <= 0:
        raise ValueError('Shares outstanding must be positive.')
    cashflows = f['FCFF'].to_numpy()
    discounted_fcff = sum(float(cf) / ((1 + wacc) ** (i + 1)) for i, cf in enumerate(cashflows))
    terminal_value = float(cashflows[-1]) * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** len(cashflows))
    ev = discounted_fcff + pv_terminal
    equity_value = ev + b.cash - b.debt  # valuation-date bridge
    return {'PV forecast FCFF': discounted_fcff, 'PV terminal value': pv_terminal,
            'Enterprise value': ev, 'Equity value': equity_value,
            'Implied price / share': equity_value / b.shares_millions,
            'Terminal value share %': pv_terminal / ev * 100 if ev else 0}
