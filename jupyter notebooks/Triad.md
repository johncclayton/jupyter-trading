# Triad Notebook Summary

## Purpose
- Implements a rules-based asset allocation screen (“Triad”) using monthly data for eight ETFs covering US equities, international equities, small/mid caps, gold, commodities, and short-duration bonds.
- Uses momentum relative to a 7-month moving average to decide which assets to hold for the coming month.
- Produces a table with four slots (S1–S4) indicating the ETF to buy for each allocation slice and a drawdown flag called `SmartLeverage`.

## Environment and Data Loading
- Libraries: numpy and pandas for numeric work, yfinance for price history, datetime/dateutil for date arithmetic, warnings/time for housekeeping.
- Date window: start fixed at `2019-01-01`; end is “tomorrow” so Yahoo Finance includes today’s close.
- Tickers (alphabetically sorted inside the code): `DBC`, `IWB`, `IWS`, `SGOL`, `VCSH`, `VGIT`, `VGSH`, `VXUS`.
- `yf.download(assets, start, end)` pulls daily OHLCV data. The notebook keeps only the Adjusted Close series and renames the columns to the ticker symbols.

## Monthly Aggregation and Moving Averages
- `data.resample('BM').last()` converts the daily adjusted closes into one row per business month-end (BM), keeping the last available price in each month.
- New columns such as `DBC_7m` or `IWB_7m` use `rolling(7).mean()` on the monthly prices to calculate a 7-observation moving average. Because the input is business-monthly, this effectively becomes a 7-month moving average.
- `pd.options.display.float_format = '{:.2f}'.format` is just for nicer numeric printing and does not affect the calculations.

## Distance-from-MA Scores
- Four empty string columns `S1`–`S4` are created to hold the eventual ETF picks.
- For every ticker a “distance” column like `IWB_dist` is defined by `(current_price - seven_month_average) / current_price`. This is approximately the percentage the ETF trades above (positive) or below (negative) its 7-month moving average.
- The loop starts at row index 8 because the first seven months have insufficient history for a 7-period rolling mean. All selections are made with `.iloc[row_index, column_index]`, relying on the column order that pandas preserves as new columns are appended.
  - Column positions relevant to the selection logic are: `S1` = index 16, `S2` = 17, `S3` = 18, `S4` = 19, and the `_dist` columns follow afterwards.

## Slot Selection Rules (per month)
1. **Safety bucket (`S4`)** – choose the bond ETF with the highest positive distance:
   - Compare `VCSH_dist`, `VGSH_dist`, and `VGIT_dist`.
   - If none beat the others decisively, it defaults to the last option checked (effectively VGIT when the other conditions fail).
2. **US core equity (`S1`)** – take `IWB` when its distance is non‑negative (price ≥ moving average); otherwise reuse the bond choice from `S4`.
3. **Style or international tilt (`S2`)** – prefer `IWS` (US mid-cap value) when its distance is non-negative and at least as large as `VXUS_dist`. Otherwise, if `VXUS_dist` is non-negative and at least as large as `IWS_dist`, pick `VXUS`. If both are negative, fall back to the bond from `S4`.
4. **Real assets (`S3`)** – compare `SGOL` (gold) and `DBC` (broad commodities) in the same fashion. If both have negative momentum, use the bond from `S4`.

The end result is that weak momentum in equities or commodities pushes that slot back into the relatively stronger bond ETF for the month.

## SmartLeverage Flag
- A new column `SmartLeverage` (index 28) starts empty.
- The code recomputes `monthlyhigh = data.resample('BM').last()` (same structure as `score`). For each month `i` it looks at the running history of `IWB` up to that point and measures the drawdown from the highest close so far:
  - `column.max()` captures the all-time high up to month `i`.
  - `column[idxmax():]` slices from the date of that high onward.
  - `min()` on that slice finds the lowest close after the high, i.e., the worst drawdown experienced since the peak.
  - If drawdown > 15% the notebook records `True` in `SmartLeverage`; otherwise `False`.
- This flag indicates when leverage (presumably handled elsewhere) should be disabled because the market is in a deep drawdown.

## Final Output Table
- `score.iloc[-24:,16:20]` keeps the most recent 24 months of selections for `S1`–`S4`.
- The index is shifted forward by one month (`index.shift(+1)`) before formatting to strings like “March 2024” so each row describes what to buy for the upcoming month.
- The index is then reset to sequential integers and the columns sorted alphabetically, causing “Month” to appear alongside `S1`–`S4` in the final display.
- A message is printed reminding the user to wait until the current month’s close and to allocate capital 1/3 to `S1`, 1/3 to `S2`, 1/6 to `S3`, and 1/6 to `S4`.
- The last cell prints the final 12 months of that table.

## Notes for Re-implementation
- Any language that can fetch historical prices, resample to monthly, compute moving averages, and perform per-row comparisons can reproduce the logic. You need:
  1. Adjusted close prices for the eight ETFs, sampled at month-end.
  2. A 7-period moving average for each series.
  3. The relative distance formula `(price - moving_avg) / price`.
  4. A monthly loop that applies the selection rules above.
  5. A drawdown routine tracking the running peak of `IWB` and flagging when the drop exceeds 15%.
- The notebook does not persist results; everything is in-memory and printed. If porting, plan how to export the final table (CSV, database, etc.).
- Beware of the reliance on column positions when using `.iloc`. If you change the column order in pandas (or another language), update the numeric indices accordingly or switch to label-based assignment.
