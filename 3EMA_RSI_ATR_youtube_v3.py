# -*- coding: utf-8 -*-
"""
17/01/2021

Code which trys to back test strategy in this video ... https://www.youtube.com/watch?v=7NM7bR2mL7U
Required info is 
- 50EMA 
- 14EMA 
- 8EMA
- Stocastic RSI (K=3, D=3, RSI_length=14, Stocastic_length=14, source=close) 
- ATR - length 14, RMA smoothing

- He was using EURUSD market, not individual stocks
- buying stocks forces you to trade n=1 stock minium, rather than always a percentage of your capital?

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

#############
Recent Changes
- Simply code to only target Long positions

TODO
- Adapt code so that when buy signal is triggered for a 15min block. Buy price is the "Open" price of the row immediately after. 
- Add or substract loss at row where a position is closed

PROBLEM 
- FINAL MONEY IS OVERWRITTEN DURING SECOND LOOP ... multiple trades could end on same row and give wrong value!

"""
#%% IMPORT LIBRARIES
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import os 

from dateutil.relativedelta import relativedelta
from datetime import datetime

#%% Stock info and manipulating dataframe section

def get_stock_info(stock_names):
    # Set the upper and lower bounds for time interval to gather data with
    # Start_date is today ... End data is two years ago, plus two days. Max range for 1h interval is 730 days = 2 years
    start_date = str(datetime.today() - relativedelta(years=2) + relativedelta(days=2)).split()[0]
    end_date = str(datetime.today()).split()[0]

    # download the data 
    df = yf.download(tickers=stock_names, start=start_date, end=end_date, interval="1h")

    # Data imported with Datetime as an index ... this resets index to integers and creates a new column showing Date
    df.reset_index(inplace=True)
    df.rename(columns={"index":"Date"}, inplace=True)
    
    return df

def calculate_EMAs (df_func):
    # Calculate EMAs using inbuilt pandas functionality 
    df_func['EMA_50'] = df_func['Adj Close'].ewm(span=50, adjust=False).mean()
    df_func['EMA_14'] = df_func['Adj Close'].ewm(span=14, adjust=False).mean()
    df_func['EMA_8'] = df_func['Adj Close'].ewm(span=8, adjust=False).mean()
    
    return df_func

def stochastic(data, k_window, d_window, window):
    # Function to get stochastic RSI
    # input to function is one column from df containing closing price or whatever value we want to extract K and D from
    
    min_val  = data.rolling(window=window, center=False).min()
    max_val = data.rolling(window=window, center=False).max()
    
    stoch = ((data - min_val) / (max_val - min_val)) * 100
    
    K = stoch.rolling(window=k_window, center=False).mean() 
    D = K.rolling(window=d_window, center=False).mean() 

    return K, D

def computeRSI (data, time_window):
    # Function to compute the RSI or Relative Strength Index for a stock. 
    # Attempts to give a person an indication if a particular stock is over- or under-sold
    
    diff = data.diff(1).dropna()        
    # diff in one field(one day)
    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rsi = 100 - 100 / (1 + abs(up_chg_avg/down_chg_avg))
    
    return rsi

def calculate_ATR(df_func):
    # Calculating ATR - Average True Range
    high_low = df_func['High'] - df_func['Low']
    high_close = np.abs(df_func['High'] - df_func['Close'].shift())
    low_close = np.abs(df_func['Low'] - df_func['Close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    df_func['ATR_14'] = true_range.rolling(14).sum()/14
    
    return df_func

def EMA_indicator (row):
    # Set the EMA_indicator column ... details whether a Long, Short or No trend is displayed
    if row['EMA_8'] > row['EMA_14'] and row['EMA_8'] > row['EMA_50'] and row['EMA_14'] > row['EMA_50']:
        return "Long"
    
    elif row['EMA_8'] < row['EMA_14'] and row['EMA_8'] < row['EMA_50'] and row['EMA_14'] < row['EMA_50']:
        return "Short"
    
    else:
        return "."

def Candle_indicator (row):
    # Set the Candle_indicator column ... details whether a Long, Short or No trend is displayed
    if row['Adj Close'] > row['EMA_8']:
        return "Long"
    
    elif row['Adj Close'] < row['EMA_8']:
        return "Short"
    
    else:
        return "."
    
def RSI_indicator (row):
    # Set the Stochastic_indicator column ... details whether a Long, Short or No trend is displayed
    # Buy signal = %K crossed above the %D
    # Sell signal = %K crossed below the %D
    if row['K'] > row['D']:
        return "Long"
    
    elif row['K'] < row['D']:
        return "Short"
    
    else:
        return "."
    
def overall_indicator (row, pos):
    # Provide overall indicator for LONG or SHORT position
    # Variable pos = "LONG" (long positions only), "SHORT" (short positions only) or "BOTH" (Long and Short positions)
    
    if pos == "LONG":
        if row['EMA_indicator'] == "Long" and row['Candle_indicator'] == "Long" and row['RSI_indicator'] == "Long":
            return "Long"
        else:
            return "-"
    
    elif pos == "SHORT":
        if row['EMA_indicator'] == "Short" and row['Candle_indicator'] == "Short" and row['RSI_indicator'] == "Short":
            return "Short"
        else:
            return "-"
    
    elif pos == "BOTH":
        if row['EMA_indicator'] == "Long" and row['Candle_indicator'] == "Long" and row['RSI_indicator'] == "Long":
            return "Long"
        elif row['EMA_indicator'] == "Short" and row['Candle_indicator'] == "Short" and row['RSI_indicator'] == "Short":
            return "Short"
        else:
            return "-"
    else:
        raise SyntaxError('Please add "pos" value - either LONG, SHORT or BOTH')
    
def calculate_annotate_indicators(df_func, pos):
    
    # Run these functions to create the new columns
    df_func['RSI_indicator'] = df_func.apply(RSI_indicator, axis=1)
    df_func['Candle_indicator'] = df_func.apply(Candle_indicator, axis=1)
    df_func['EMA_indicator'] = df_func.apply(EMA_indicator, axis=1)
    
    # Annotate with overall indicator column, all three indicators must be either Long or Short
    df_func['Indicator'] = df_func.apply(overall_indicator, pos=pos, axis=1) 
    
    return df_func

#%% PLOTTING SECTION
from EMA_RSI_ATR_plotting_functions import plot_price, plot_stoch_RSI, plot_ATR, plot_candlestick

def plot_all(data):  
    plot_price(data)
    #plot_RSI(data)
    plot_stoch_RSI(data)
    plot_ATR(data)
    plot_candlestick(data)
    return None 

#%% Inspect outcomes, to be run almost interactively

def inspect_winrate(df_func, stock_names):

    df_func.Outcome.value_counts()
    
    # Overall Winrate
    winrate = 100*(df_func.Outcome.str.count("Win").sum() / (df_func.Outcome.str.count("Win").sum() + df_func.Outcome.str.count("Loss").sum()))
    n_trades = df_func.Outcome.str.count("Win").sum() + df_func.Outcome.str.count("Loss").sum() 
    
    print(f"Overall Winrate for {stock_names} = {winrate:.1f} %")
    print(f"Total Number of Trades {stock_names} = {n_trades}")

    return None

#%% Define the main function of the programme
def main():
    
    # Set working directory
    working_d = "C:\\Users\\cns\\Documents\\PythonCode\\shares_rolling_av_strat\\Stock_market_trader_EMA_RSI_ATR"
    os.chdir(f"{working_d}")
    
    # Create dataframe with stock prices (1hr scale, 2 year)
    stock_names = "VLX.L"
    df = get_stock_info(stock_names)
        
    # Generate EMAs
    df = calculate_EMAs (df_func=df)
    
    # Generate RSI data and the Stocastic RSI data - time_window in YouTube video is 14
    df['RSI'] = computeRSI(data=df['Adj Close'], time_window=14)
    df['K'], df['D'] = stochastic(data=df['RSI'], k_window=3, d_window=3, window=14)
    
    # Generate ATR14
    df = calculate_ATR(df_func=df)
    
    # Calculate and annotate with indicators
    # Variable pos = "LONG" (long positions only), "SHORT" (short positions only) or "BOTH" (Long and Short positions)
    df = calculate_annotate_indicators(df_func=df, pos="LONG")
    
    # Store a copy of the unmodified dataframe for Troubleshooting
    df_temp = df.copy(deep=True)
    
    # Step-wise backtesting method 
    from EMA_RSI_ATR_backtest_function_one import backtest_step_one
    from EMA_RSI_ATR_backtest_function_two import backtest_step_two
    
    df = df_temp.copy(deep=True)
    df = backtest_step_one(df_func=df, max_positions=1)
    df = backtest_step_two(df_func=df, pot_size=1000, position_size=0.02, transaction_fee=2.95, stamp_duty=0)
    
    # Check final row's Final Money value
    print(df.iloc[-1]['Final Money (£)'])
    
    df.columns
    df["Profit/Loss on Sales (£)"].sum()
    df['N_shares_purchased'].sum()*transaction_fee
    df["Profit/Loss on Sales (£)"].sum()
    
    # Make the desired plots
    plot_all(data=df)
        
    # TODO 
    # Change it to have two iterations ... first cycle through the dataframe highlights all of the possible longs/shorts and exit rows
    # Second pass or possible end of first, can calculate the costs of trade and profit of trade. 
    # Third or second pass can trim dataframe down to action rows, and have some kind of counter feature much more easily
    # Plots to show wins and losses through time etc

    # Print the winrate statistics to console
    inspect_winrate(df_func=df, stock_names=stock_names)
    
    # Plot All The Things
    plot_all(data=df)
    
    # Save the results
    # in full
    df.to_csv(f"{working_d}\\VOLEX_results_ii_fee.tsv", sep="\t")
    # trimmed version
    df[['Date','Open','High','Low','Adj Close','Volume','Indicator','Initial Money (£)','Final Money (£)','Profit/Loss (£)',
        'Target','StopLoss','N_shares_purchased','Money_spent_on_shares','Outcome','Exit Row']].to_csv(f"{working_d}\\VOLEX_results_ii_fee.tsv", sep="\t")

if __name__ == "__main__":
    main()