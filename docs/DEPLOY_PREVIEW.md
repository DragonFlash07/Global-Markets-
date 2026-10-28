# Review and deploy the preview

Repository: DragonFlash07/Global-Markets-
Review branch: improve-market-layout-separate-dcf
Main file path: app.py
Python: 3.12

In Streamlit Community Cloud select Create app and use the repository, review branch and app.py. Deploy this branch as a separate preview so the existing main-branch app remains available. Streamlit reads the project from GitHub; no manual Python-file upload is required. Do not deploy only app.py: core/, pages/, data/, requirements.txt and .streamlit configuration are part of the app.

Review order:
1. Company financials: BHP and Reliance Jio Infocomm FY2024–FY2026 history, reporting currencies, scopes, units and source links.
2. Three-statement modelling: opening FY2026 balances load from the source snapshot. Confirm scope; inspect annual editable assumptions and the checks tab. Forecast defaults are flat revenue and historic cost/working-capital proxies, not company guidance. Other balance-sheet items are held constant.
3. DCF: review WACC assumptions and equity bridge. The valuation date is the opening fiscal-year end, not today's date. Annual year-end discounting is used.
4. Jio common-equity/per-share values are withheld pending convertible-preference and debt/lease/spectrum analysis. Enterprise value is a simplified scenario estimate.
5. BHP reports in USD; no automatic AUD market-price comparison is performed.

Current limitations: snapshots are manually transcribed and reconciled, not an automatic live filing ingest; quarterly results are not included. Forecasts do not yet include full commodity/subscriber schedules, deferred-tax/asset-vintage schedules, full historical-to-forecast accounting mapping or a valuation-date fully diluted capital structure. Do not interpret this preview as a completed investment recommendation.

No CFI course workbooks/PDFs or credentials are committed.
