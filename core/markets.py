"""Static demo universes; replace with regularly maintained full index constituent lists."""
INDIA = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BHARTIARTL.NS",
    "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "ETERNAL.NS",
    "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS",
    "ITC.NS", "JIOFIN.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SHRIRAMFIN.NS",
    "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS",
]
USA = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "BAC", "V", "MA", "WMT", "COST", "UNH", "LLY", "AVGO", "AMD", "CRM", "NFLX", "XOM", "CVX", "KO", "PEP", "DIS", "CAT"]
ASX = ["BHP.AX", "CBA.AX", "CSL.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "WES.AX", "WOW.AX", "MQG.AX", "RIO.AX", "FMG.AX", "WDS.AX", "TCL.AX", "ALL.AX", "GMG.AX", "TLS.AX", "COL.AX", "S32.AX", "QBE.AX", "STO.AX"]
GOLD = ["GC=F", "GLD", "IAU", "GOLD.AX"]  # futures + ETFs; distinct instruments/currencies
MARKETS = {
    "India · NSE sample": {"symbols": INDIA, "timezone": "Asia/Kolkata", "currency": "INR", "indices": {"Nifty 50": "^NSEI", "Sensex": "^BSESN", "Bank Nifty": "^NSEBANK", "Nifty IT": "^CNXIT"}, "default": "RELIANCE.NS"},
    "USA · liquid-stock sample": {"symbols": USA, "timezone": "America/New_York", "currency": "USD", "indices": {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Russell 2000": "^RUT"}, "default": "AAPL"},
    "Australia · ASX sample": {"symbols": ASX, "timezone": "Australia/Sydney", "currency": "AUD", "indices": {"ASX 200": "^AXJO"}, "default": "BHP.AX"},
    "Gold · futures and ETFs": {"symbols": GOLD, "timezone": "America/New_York", "currency": "Mixed", "indices": {"Gold futures · USD/oz": "GC=F", "GLD ETF · USD/share": "GLD"}, "default": "GC=F"},
}
