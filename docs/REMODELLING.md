# Research model rebuild

## Working status
Local implementation: explicit opening balances, annual forecasts, cash/financing schedules, tax-loss carry-forward, separate FCFF and DCF. Company research targets are BHP Group and Reliance Jio Infocomm Limited (not Jio Financial Services, Jio Platforms or Reliance Industries). Existing market/chart pages remain.

No official company financial amounts have been imported or validated yet. Company mode requires manually entered opening balances and a source reference. The source reference and checkbox are analyst attestations, not an automated audit. Synthetic examples are explicitly labelled.

## Sources to map next
- BHP annual reports: https://www.bhp.com/annualreport
- Jio entity financials: https://www.jio.com/about/investor-relations/financials/

Collect three historical fiscal years with consistent consolidated/standalone scope, currencies, units and restatements. Reconcile all assets/liabilities/equity, cash movements and debt (including appropriate lease/spectrum treatment). Do not substitute a parent ticker or parent diluted shares for the modelled entity. BHP reporting currency and ASX quotation currency need an explicit FX bridge before market-price comparison.

BHP: segment production volumes, realised commodity prices, unit costs, royalties, sustaining/growth capex, closure liabilities and non-controlling interests. Jio: subscribers, average revenue per user, service/other revenue, network capex, spectrum/infrastructure obligations and financing. Segment schedules are not implemented yet; annual growth and cost ratios currently require analyst input.

## Conventions and limitations
- All monetary amounts/shares in millions, single currency per model.
- Explicit other assets and other liabilities; no forced opening residual.
- Interest on opening term debt plus opening revolver. This deliberately differs from the CFI iterative average-balance model and does not claim workbook equivalence.
- Debt and equity changes, dividends, capex and depreciation are annual absolute inputs.
- Revolver draws/repays within a declared facility; unmet minimum cash blocks valuation in the UI.
- Cash tax accounting: tax and accounting depreciation are identical, no deferred taxes; losses carried forward indefinitely without jurisdictional limits. This is a simplified engine.
- Other balance-sheet categories held constant; no asset disposals or changes in share count.
- DCF supports finite annual flows, normalized next-year terminal FCFF or EBITDA exit multiple, explicit bridge and dilution denominator. Engine supports actual/365 cash-flow dates; UI currently uses year-end annual periods.
- WACC defaults and scenario seed drivers are illustrative, not sourced estimates.
- CFI course files are private reference materials and must not be committed to public source.

## Acceptance still outstanding
Full CFI workbook scenario/tax/financing parity, sourced company historical mapping, sector schedules, FX/market-price comparison, persistence across independent sessions, live data and browser visual checks. Existing repository review reports a separately tested 32-test implementation; that code has not been supplied here and is not overwritten or claimed recovered.

## Environment handoff
This workspace is not the Windows OneDrive folder. Share source through Git and use a single branch/commit as the coding baseline. Keep privately licensed reference files outside the public repository. A separate Codex session needs those references attached or granted as local folder access; seeing a chat does not establish identical filesystem access.
