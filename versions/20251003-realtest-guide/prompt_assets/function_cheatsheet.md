# RealTest Language Cheat Sheet

Summaries derived from function_catalog.json; one-liners are truncated for prompt friendliness.

## #Avg
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.1
- Summary: For each date, evaluates a formula and calculates the average value for all symbols on that date.
- Example: `InduFactor:	#Avg #ByIndu StockFactor	// factor values averaged by industry` (samples/gics_indu_rank.rts:18)

## #ByCII
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.2
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of stocks that share the same corresponding industry index
- Example: `// use "#ByCII" after any breadth tag to calculate separately for each CII group` (samples/cii_rotate.rts:32)
- See also: ?CII, CIIFamily, and CIILevel.See the cii_rotate.rts sample script for a complete

## #ByEcon
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.3
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of stocks that share the same economic sector name
- Example: `SectFactor:	#Avg #ByEcon StockFactor` (samples/sector_etfs_breadth.rts:41)

## #ByGroup
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.4
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of stocks that share the same industry group name

## #ByIndu
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.5
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of stocks that share the same industry name
- Example: `InduFactor:	#Avg #ByIndu StockFactor	// factor values averaged by industry` (samples/gics_indu_rank.rts:18)

## #ByListNum
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.6
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for the stocks from each separate Include List

## #ByMkt
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.7
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of individual futures contracts within the same market.
- Example: `AgeRank:	#Rank #ByMkt -DaysToExp` (samples/futures_calendar_spread.rts:18)

## #BySect
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.8
- Summary: A secondary cross-sectional function, which requests that the primary function be calculated separately for each group of stocks that share the same business sector name

## #Count
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.9
- Summary: For each date, calculates the count of symbols for which a formula can be evaluated on that date.
- Example: `total:	#count 1` (samples/breadth.rts:19)

## #DenseRank
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.10
- Summary: For each date, evaluates a formula and then calculates the dense rank of each symbol's value among all symbols on that date. Lowest rank (1) means highest value. Identical values get the same rank…

## #Highest
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.11
- Summary: For each date, evaluates a formula and calculates the highest (largest) value for all symbols on that date.
- Example: `CL1:	#Highest if(AgeRank=1, Symbol, 0)` (samples/cl_term_structure.rts:16)

## #Lowest
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.12
- Summary: For each date, evaluates a formula and calculates the lowest (smallest) value for all symbols on that date.
- Example: `StockInduRank:	#Lowest #ByIndu InduRank	// the industry rank of each stock` (samples/gics_indu_rank.rts:21)

## #Median
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.13
- Summary: For each date, evaluates a formula and calculates the median value for all symbols on that date.
- Example: `MedC:	#Median C` (samples/index_breadth.rts:15)

## #OnePerDate
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.14
- Summary: Evaluate this Data or Test Data formula only once per date and return this value for any stock that references the item
- Example: `LTGain:	#OnePerDate if(SinceEOY > 0, Combined(TradeStatSum(if(DateYear(T.DateOut) = This(Year) and Days(T.DateIn, T.DateOut) > 366, T.Profit - T.Div, 0))), 0)` (samples/annual_taxes.rts:13)
- See also: #One Per Sym.Add both #One Per Date and #One Per Sym to calculate and store only a single value for all bars of all stocks (this is done automatically for constants and constant expressions).

## #OnePerSym
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.15
- Summary: Evaluate this Data or Test Data formula only once per symbol and return this same value for all bars.
- See also: #One Per Date.Add both #One Per Date and #One Per Sym to calculate and store only a single value for all bars of all stocks (this is done automatically for constants and constant expressions).

## #PercentRank
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.16
- Summary: For each date, evaluates a formula and then calculates the percent rank of each symbol's value among all symbols on that date.
- Example: `Percentile:	#PercentRank 100 * CanRank + AdjSlope` (samples/clenow_stocks_on_move.rts:37)

## #Rank
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.17
- Summary: For each date, evaluates a formula and then calculates the rank of each symbol's value among all symbols on that date. Lowest rank (1) means highest value. Identical values get different rank numbers.
- Example: `InduRank:	#Rank if(ListNum=99, ROC30, nan) // rank the index ETFs by the factor` (samples/cii_rotate.rts:27)

## #SlowCalc
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.18
- Summary: #Slow Calc is a special Data Section tag that looks like a cross-sectional function name but is not one.Specifying #Slow Calc at the beginning of a Data formula tells Real Test to NOT use the…
- Example: `// AdjSlope calculation (#SlowCalc is required because log(c) of unadjusted prices can't be buffered)` (samples/clenow_stocks_on_move.rts:30)
- See also: Split Handling, particularly the

## #StdDev
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.19
- Summary: For each date, evaluates a formula and then calculates the standard deviation of values among all symbols on that date.

## #Sum
- Category: Cross-Sectional Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.20
- Summary: For each date, evaluates a formula and calculates the sum of values for all symbols on that date.
- Example: `numob:	#sum ob` (samples/breadth.rts:20)

## ?Strategy
- Category: Current Strategy Information
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.37
- Summary: Name of the current strategy
- See also: Strat Num, which returns the current strategy's number, and Strat Ref, which allows dynamic strategy lookup.

## ?StratType
- Category: Current Strategy Information
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.38
- Summary: Type of the current strategy

## Abs
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.42
- Summary: Absolute Value of a number
- Example: `CanRank:	InSPX and C > MA(C,100) and CountTrue(ABS(ROC(C,1))>=15, 90) == 0` (samples/clenow_stocks_on_move.rts:36)

## ADX
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.46
- Summary: Wilder's Average Directional Index
- Example: `adx7:	adx(7)` (samples/bensdorp_book.rts:34)

## AEMA
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.47
- Summary: Adaptive Exponential Moving Average

## AESD
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.48
- Summary: Adaptive Exponential Standard Deviation

## Allocation
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.49
- Summary: Dollars allocated to this strategy Input Any formula specifying a dollar amount
- Example: `Quantity:	30 	// 30% allocation to one ETF` (samples/combined.rts:31)

## AllowMissingBar
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.50
- Summary: Whether to allow backtests to enter and exit positions after missing bars Input True or False (default is False)
- See also: the general topic of Calendar Alignment and the Missing Bars function, which can be used to count missing bars.

## AllowNoVolume
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.51
- Summary: Whether to allow backtests to enter and exit positions on bars with zero volume Input True or False (default is False)

## Ambiguity
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.54
- Summary: Specifies what assumptions to make when there is price sequence ambiguity in a test Choices Default - assume that if Close > Open then Low preceded High, or if Close < Open then High preceded Low…

## ArcCos
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.55
- Summary: Determines which angle has the specified Cosine

## ArcSin
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.56
- Summary: Determines which angle has the specified Sine

## ArcTan
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.57
- Summary: Determines which angle has the specified Tangent

## Assert
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.59
- Summary: Require a condition to be true for the script to continue

## ATR
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.60
- Summary: Wilder's Average True Range
- Example: `atr10:	atr(10)` (samples/bensdorp_book.rts:29)

## BBBot
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.67
- Summary: Bollinger band bottom
- Example: `BBL:  	BBBOT(100,1)` (samples/radge_bbo.rts:32)

## BBBotF
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.68
- Summary: Bollinger band bottom as a function

## BBPct
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.69
- Summary: Bollinger band percent (%B)

## BBPctF
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.70
- Summary: Bollinger band percent (%B) as a function

## BBTop
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.71
- Summary: Bollinger band top
- Example: `BBH:  	BBTOP(100,3)` (samples/radge_bbo.rts:31)

## BBTopF
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.72
- Summary: Bollinger band top as a function

## BBTrend
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.73
- Summary: Bollinger band trend

## BBTrendF
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.74
- Summary: Bollinger band trend as a function

## BBWidth
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.75
- Summary: Bollinger band width

## BBWidthF
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.76
- Summary: Bollinger band width as a function

## Bound
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.78
- Summary: Force a value to be between a lower and upper limit
- Example: `slopescore:	0.5 * (Bound(pposlope, -1, 1) + 1)` (samples/sctr.rts:20)

## CalendarSym
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.79
- Summary: Symbol to use as the market date list for this strategy Input Any symbol in the current data file (does not require an extra $)
- See also: the general topic of Calendar Alignment.

## CCI
- Category: Indicator Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.85
- Summary: Commodity Channel Index of this indicator, see its Stock Charts Chart School page.

## CDF
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.86
- Summary: Cumulative Distribution Function

## CloseSlip
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.92
- Summary: Slippage amount, in points (dollars per share or contract), for each transaction that simulates a market order filling at the close Input Any formula specifying dollars per share or contract (points)

## Commission
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.96
- Summary: Commission amount, in instrument or account currency units, for each trade Input Formula specifying a commission amount
- Example: `Commission:	Max(0.005 * Shares, 1)` (samples/bensdorp_book.rts:91)

## Compounded
- Category: Strategy Elements
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.97
- Summary: Optionally overrides the automatically-determined S.Compounded flag for a strategy Choices True - force the strategy to report stats as if compounded False - force the strategy to report stats as…
- Example: `Allocation:	S.StartEquity // non-compounded` (samples/dividend_capture.rts:43)
- See also: Compounding.

## Correl
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.99
- Summary: Pearson's Correlation of two series
- Example: `R2:	#SlowCalc Correl(Log(C), FunBar, lookback) ^ 2` (samples/clenow_stocks_on_move.rts:33)
- See also: Spearman, Correl Avg, etc.

## CorrelAvg
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.100
- Summary: Average correlation of a stock to a group of stocks
- Example: `Demonstrates how to use CorrelAvg and related functions` (samples/correl_multi.rts:2)
- See also: Correl, Spearman, Correl Med, Correl Min, Correl Min Sym, Correl Max, Correl Max Sym

## CorrelMax
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.104
- Summary: Highest correlation of a stock to a group of stocks
- Example: `corr_max:	CorrelMax(InDJI, factor, len, sprmn)` (samples/correl_multi.rts:31)
- See also: Correl, Spearman, Correl Avg, Correl Med, Correl Min, Correl Min Sym, Correl Max Sym

## CorrelMaxSym
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.105
- Summary: Symbol of stock with highest correlation to the current stock
- Example: `corr_max_sym:	CorrelMaxSym(InDJI, factor, len, sprmn)` (samples/correl_multi.rts:32)
- See also: Correl, Spearman, Correl Avg, Correl Med, Correl Min, Correl Min Sym, Correl Max

## CorrelMed
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.101
- Summary: Median correlation of a stock to a group of stocks
- Example: `corr_med:	CorrelMed(InDJI, factor, len, sprmn)` (samples/correl_multi.rts:28)
- See also: Correl, Spearman, Correl Avg, Correl Min, Correl Min Sym, Correl Max, Correl Max Sym

## CorrelMin
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.102
- Summary: Lowest correlation of a stock to a group of stocks
- Example: `corr_min:	CorrelMin(InDJI, factor, len, sprmn)` (samples/correl_multi.rts:29)
- See also: Correl, Spearman, Correl Avg, Correl Med, Correl Min Sym, Correl Max, Correl Max Sym

## CorrMinSym
- Category: Multi-Bar Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.103
- Summary: Symbol of stock with lowest correlation to the current stock
- Example: `CorrMinSym:	Extern(SymNum(corr_min_sym), ?Symbol)` (samples/correl_multi.rts:41)
- See also: Correl, Spearman, Correl Avg, Correl Med, Correl Min, Correl Max, Correl Max Sym

## Cosine
- Category: General-Purpose Functions
- Manual path: Realtest Script Language > Syntax Element Details / 17.18.106
- Summary: Trigonometric cosine of a number of degrees
- Example: `hannfunc:	(1 - Cosine(360 * FunBar / (len+1)))` (samples/ehlers_windows.rts:22)
