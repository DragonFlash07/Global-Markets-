import numpy as np
import pandas as pd


def indicators(df: pd.DataFrame) -> pd.DataFrame:
    h = df.copy()
    c = h['Close'].astype(float)
    h['SMA20'] = c.rolling(20).mean()
    h['SMA50'] = c.rolling(50).mean()
    h['EMA12'] = c.ewm(span=12, adjust=False).mean()
    h['EMA26'] = c.ewm(span=26, adjust=False).mean()
    h['BB upper'] = h['SMA20'] + 2 * c.rolling(20).std()
    h['BB lower'] = h['SMA20'] - 2 * c.rolling(20).std()
    diff = c.diff()
    gain = diff.clip(lower=0).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    loss = (-diff.clip(upper=0)).ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    h['RSI'] = 100 - 100/(1 + rs)
    h['MACD'] = h['EMA12'] - h['EMA26']
    h['MACD signal'] = h['MACD'].ewm(span=9, adjust=False).mean()
    h['MACD hist'] = h['MACD'] - h['MACD signal']
    if 'Volume' in h.columns:
        typical = (h['High'] + h['Low'] + c)/3
        # Session-reset VWAP works on intraday feeds; on daily candles it is not used.
        idx = h.index
        if isinstance(idx, pd.DatetimeIndex) and idx.tz is not None:
            groups = idx.date
        else:
            groups = pd.DatetimeIndex(idx).date
        numerator = (typical * h['Volume']).groupby(groups).cumsum()
        denominator = h['Volume'].groupby(groups).cumsum().replace(0, np.nan)
        h['VWAP'] = numerator / denominator
    return h
