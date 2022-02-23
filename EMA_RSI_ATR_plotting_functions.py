# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 14:01:02 2022

@author: cns

Part of the EMA_RSI_ATR_youtube.py scripts
Contains all the plotting functions for displaying the stock market data 
- price and EMAS over time
- Stochastic RSI over time
- ATR over time
- Candlestick plots over time

"""
import matplotlib.pyplot as plt

def plot_price(data):
    # plot price
    plt.figure(figsize=(15,5))
    plt.plot(data.index, data['Adj Close'])
    plt.plot(data.index, data['EMA_50'], label='EMA_50')
    plt.plot(data.index, data['EMA_14'], label='EMA_14')
    plt.plot(data.index, data['EMA_8'], label='EMA_8')
    plt.title('Price chart (Adj Close)')
        
    plt.legend(loc='best')
    plt.show()
    return None

def plot_RSI(data):
    # plot correspondingRSI values and significant levels
    plt.figure(figsize=(15,5))
    plt.title('RSI chart')
    plt.plot(data.index, data['RSI'], label='RSI')

    plt.axhline(0, linestyle='--', alpha=0.1)
    plt.axhline(20, linestyle='--', alpha=0.5)
    plt.axhline(30, linestyle='--')

    plt.axhline(70, linestyle='--')
    plt.axhline(80, linestyle='--', alpha=0.5)
    plt.axhline(100, linestyle='--', alpha=0.1)
    
    plt.legend(loc='best')
    plt.show()
    return None

def plot_stoch_RSI(data):
    # plot corresponding Stoch RSI values and significant levels
    plt.figure(figsize=(15,5))
    plt.title('stochRSI chart')
    plt.plot(data.index, data['K'], label='RSI_K')
    plt.plot(data.index, data['D'], label='RSI_D')

    plt.axhline(0, linestyle='--', alpha=0.1)
    plt.axhline(20, linestyle='--', alpha=0.5)
    #plt.axhline(30, linestyle='--')

    #plt.axhline(70, linestyle='--')
    plt.axhline(80, linestyle='--', alpha=0.5)
    plt.axhline(100, linestyle='--', alpha=0.1)
    
    plt.legend(loc='best')
    plt.show()
    return None

def plot_ATR(data):
    
    # Plot the ATR for given time period
    plt.figure(figsize=(15,5))
    plt.title('ATR Chart')
    
    plt.plot(data.index, data['ATR_14'].fillna(0), label='ATR_14')   # NaN to zeros so plot is in scale
    plt.legend(loc='best')
    plt.show()
    return None

def plot_candlestick(data):
    
    #create figure
    plt.figure(figsize=(15,5))
    plt.title('Candlestick Chart')
    
    #define width of candlestick elements
    width_main = .05
    width_tail = .01

    #define up and down prices
    up = data[data['Adj Close']>=data['Open']]
    down = data[data['Adj Close']<data['Open']]

    #define colors to use
    col1 = 'green'
    col2 = 'red'

    #plot up prices
    plt.bar(up.index, height=(up['Adj Close'] - up['Open']), width=width_main, bottom=up['Open'], color=col1)
    plt.bar(up.index, height=(up['High'] - up['Adj Close']), width=width_tail, bottom=up['Adj Close'], color=col1)
    plt.bar(up.index, height=(up['Low'] - up['Open']), width=width_tail, bottom=up['Open'], color=col1)

    #plot down prices
    plt.bar(down.index, height=(down['Adj Close'] - down['Open']), width=width_main, bottom=down['Open'], color=col2)
    plt.bar(down.index, height=(down['High'] - down['Open']), width=width_tail, bottom=down['Open'], color=col2)
    plt.bar(down.index, height=(down['Low'] - down['Adj Close']), width=width_tail, bottom=down['Adj Close'], color=col2)
    
    #add emas
    plt.plot(data.index, data['EMA_50'], label='EMA_50')
    plt.plot(data.index, data['EMA_14'], label='EMA_14')
    plt.plot(data.index, data['EMA_8'], label='EMA_8')

    #rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    #display candlestick chart
    plt.legend(loc='best')
    plt.show()
    return None
