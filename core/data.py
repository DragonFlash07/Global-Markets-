"""Yahoo/yfinance demo data. Not real-time or licensed for a public commercial feed."""
import pandas as pd
import streamlit as st
import yfinance as yf


def _closes(raw: pd.DataFrame, tickers: tuple[str, ...]) -> pd.DataFrame:
    """Normalize yfinance columns, including single-ticker downloads."""
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            return pd.DataFrame()
        result = raw["Close"].copy()
        if isinstance(result, pd.Series):
            return result.to_frame(name=tickers[0])
        return result
    if "Close" in raw:
        return raw[["Close"]].rename(columns={"Close": tickers[0]})
    return pd.DataFrame()


def build_mover_table(daily: pd.DataFrame, intraday: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """Compare last available intraday bar with prior *session* close (fallback daily)."""
    records = []
    for symbol in daily.columns:
        d = daily[symbol].dropna()
        if len(d) < 2:
            continue
        price, reference = float(d.iloc[-1]), float(d.iloc[-2])
        source = "daily close"
        stamp = str(d.index[-1])[:10]
        if symbol in intraday.columns:
            live = intraday[symbol].dropna()
            if not live.empty:
                last_ts = live.index[-1]
                if last_ts.tzinfo is not None:
                    last_ts = last_ts.tz_convert(timezone)
                intraday_date = last_ts.date()
                dates = [idx.tz_convert(timezone).date() if idx.tzinfo else idx.date() for idx in d.index]
                preceding = d.loc[[dt < intraday_date for dt in dates]]
                if not preceding.empty:
                    price = float(live.iloc[-1])
                    reference = float(preceding.iloc[-1])
                    source = "latest 5m bar"
                    stamp = str(last_ts)
        if reference > 0:
            records.append({"Symbol": symbol, "Last": price, "Previous close": reference,
                            "Change %": 100 * (price / reference - 1),
                            "Source": source, "As of": stamp})
    return pd.DataFrame(records)


@st.cache_data(ttl=290, show_spinner=False)
def movers(symbols: tuple[str, ...], timezone: str) -> pd.DataFrame:
    try:
        raw_day = yf.download(list(symbols), period="10d", interval="1d", progress=False,
                              group_by="column", auto_adjust=False, threads=True)
        day = _closes(raw_day, symbols)
        if day.empty:
            return pd.DataFrame()
        try:
            raw_intra = yf.download(list(symbols), period="2d", interval="5m", progress=False,
                                    group_by="column", auto_adjust=False, threads=True)
            intra = _closes(raw_intra, symbols)
        except Exception:
            intra = pd.DataFrame()
        return build_mover_table(day, intra, timezone)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=290, show_spinner=False)
def candles(symbol: str, period: str, interval: str) -> pd.DataFrame:
    try:
        return yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def statements(symbol: str):
    try:
        t = yf.Ticker(symbol)
        return t.income_stmt, t.balance_sheet, t.cashflow
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
