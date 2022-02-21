# Stock_market_trader_EMA_RSI_ATR
 Python code for stock market trading, indicating BUY/SELL signals using EMA, stochastic RSI and ATR.

Code which trys to back test strategy in this video ... https://www.youtube.com/watch?v=7NM7bR2mL7U
Required info is 
- 50EMA 
- 14EMA 
- 8EMA
- Stocastic RSI (K=3, D=3, RSI_length=14, Stocastic_length=14, source=close) 
- ATR - length 14, RMA smoothing

# For a Long position 
(1) 8EMA > 14EMA > 50EMA, indicates upward trend
(2) Stocastic cross over
(3) Adj Close > all EMAs

Target is 2 x ATR value, stop loss is 3 x ATR value

# For a short position
(1) 8EMA < 14EMA < 50EMA
(2) Stocastic cross over
(3) Close < all EMAs

Target 2 x ATR value, stop loss is 3 x ATR value.

#############
He reported a 76% win rate over 100 trades ... lets find out if I get the same 
The adjusted closing price amends a stock's closing price to reflect that stock's value after accounting for any corporate actions (stock splits, dividends etc)
More accurate reflection of the value of the stock at the historical time
Use this instead of Close price, better for back testing.

Repository contains
(1) Main python code
(2) python file containing a function which only runs strategy with long positions and introducing fees (estimated from Fineco Account - £2.95 per UK market trade)
(3) Example results folder for VOLEX.
