# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:21:38 2022

@author: cns

# Variables 
df_func, dataframe with data in it
position_size, percentage of capital pot to enter into each position - 0.02 = 2%
pot_size, capital started with £1000
transaction_fee, fee of a transaction
stamp_duty, stamp duty tax associated with some FTSE100 companies

"""
def backtesting_function(df_func, position_size, pot_size, transaction_fee, stamp_duty):
    
    import pandas as pd
    import numpy as np
    import math
    
    # Deal with Long and Short separately.
    # Start with a pot of £1000 and only investing 2% of your portfolio
    # Assume entry and midpoint = High - [(High-Low)/2]
    
    # position_size = percentage of capital you wish to invest in each position - e.g. 0.02 = 2%
    # pot_size = starting capital (£) 
    # transaction_fee = cost of each transaction 
    # stamp_duty = stamp duty due with some FTSE100 companies?
    
    for index1, row1 in df_func.iterrows():
        
        if index1 == 0:
            # TODO - Add something more sophisticated here, what if Long indicator triggered in first row.
            df_func.loc[index1,"Initial Money (£)"] = round(pot_size,2)
            df_func.loc[index1,"Final Money (£)"] = round(pot_size,2)
            df_func.loc[index1,"Profit/Loss (£)"] = None
            continue
        else:
            df_func.loc[index1,"Initial Money (£)"] = round(df_func.loc[(index1-1),"Final Money (£)"],2)
        
        # If preceding row's indicator signal was "-", no trades to enter in this row, so just create final money value with any prior profit/loss values
        if df_func.loc[(index1-1),"Indicator"] == "-":
            # If profit/loss column is null, no prior trades exited here, so final money = initial money
            if pd.isnull(df_func.loc[index1,"Profit/Loss (£)"]):
                df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,"Initial Money (£)"],2)  
            # If profit/loss column isn't null, prior trades have exited here, final money = initial money +/- prior trade profit/loss
            elif pd.notnull(df_func.loc[index1,"Profit/Loss (£)"]):
                df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,"Initial Money (£)"] + df_func.loc[index1,"Profit/Loss (£)"], 2)
            continue
        
        # If preceding row's indicator signal was LONG signal, buy into long and create second iteration through rows to see outcome
        elif df_func.loc[(index1-1),"Indicator"] == "Long":

            ### PURCHASE SECTION ### 
            
            # Set Target and StopLoss Variables, based on Open price of subsequent time block.
            # Cannot yet calculate ATR value for this time block, so use preceding row1.ATR_14 value
            Target = float(df_func.loc[index1,"Open"] + 2*df_func.loc[(index1-1),'ATR_14'])
            StopLoss = float(df_func.loc[index1,"Open"] - 3*df_func.loc[(index1-1),'ATR_14'])
            # Create dataframe row values for these for later reference in results table
            df_func.loc[index1,"Target"] = round(Target,2)
            df_func.loc[index1,"StopLoss"] = round(StopLoss,2)
            
            # Calculate nshares bought and money spent on the position (inc. transaction fee)
            # NB: nshares can only be an integer value!
            nshares_purchased = position_size*df_func.loc[index1,"Initial Money (£)"] / df_func.loc[index1,"Open"]
            
            print(nshares_purchased)
            if nshares_purchased < 1:
                nshares_purchased = 1
            elif nshares_purchased > 1:
                nshares_purchased = np.floor(nshares_purchased)
            print(nshares_purchased)
            
            df_func.loc[index1, "N_shares_purchased"] = nshares_purchased
            df_func.loc[index1, "Money_spent_on_shares"] = nshares_purchased*df_func.loc[index1,"Open"]
            money_spent = (nshares_purchased*df_func.loc[index1,"Open"]) + transaction_fee
            
            # If profit/loss column is null, no prior trades exited here
            if pd.isnull(df_func.loc[index1,"Profit/Loss (£)"]):
                # set value of profit/loss = cost of new trade
                df_func.loc[index1,"Profit/Loss (£)"] = round(money_spent, 2)
                # and set value of final money = initial money - money spent on new trade
                df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,"Initial Money (£)"] - money_spent, 2)
            # If profit/loss column isn't null, prior trades have also exited here
            elif pd.notnull(df_func.loc[index1,"Profit/Loss (£)"]):
                # so update the final value of profit/loss to include cost of new trade
                df_func.loc[index1,"Profit/Loss (£)"] = round(df_func.loc[index1,"Profit/Loss (£)"] - money_spent,2)
                # and set value of final money = initial money +/- updated profit/loss value 
                df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,"Initial Money (£)"] + df_func.loc[index1,"Profit/Loss (£)"], 2)
            
            ### RESULT SECTION ###
            
            # Want to then iterate through dataframe from that point on
            # See where trades ended and place all the profit/loss into the sale row's Final Money column
            for index2, row2 in df_func.loc[index1:].iterrows():
                
                if row2.High > Target:
                    # Record on the purchase row (index1) if it was a Long - Win and show sale row (index2).
                    df_func.loc[index1,"Outcome"] = "Long - Win"
                    df_func.loc[index1,"Exit Row"] = row2.name
                    
                    # Record on the sale row (index2) how much money was made, by either creating profit/loss value or updating it
                    profit = nshares_purchased*Target - transaction_fee
                    if pd.isnull(df_func.loc[index2,"Profit/Loss (£)"]):
                        df_func.loc[index2,"Profit/Loss (£)"] = round(profit,2)
                    elif pd.notnull(df_func.loc[index2,"Profit/Loss (£)"]):
                        df_func.loc[index2,"Profit/Loss (£)"] = round(df_func.loc[index2,"Profit/Loss (£)"] + profit,2)
                    break 
                    
                elif row2.Low < StopLoss:
                    # Record on the purchase row (index1) if it was a Long - Loss and show sale row (index2).
                    df_func.loc[index1,"Outcome"] = "Long - Lost"
                    df_func.loc[index1,"Exit Row"] = row2.name
                    
                    # Record on the sale row (index2) how much money was made, by either creating profit/loss value or updating it.
                    loss = nshares_purchased*StopLoss + transaction_fee
                    if pd.isnull(df_func.loc[index2,"Profit/Loss (£)"]):
                        df_func.loc[index2,"Profit/Loss (£)"] = round(loss,2)
                    elif pd.notnull(df_func.loc[index1,"Profit/Loss (£)"]):
                        df_func.loc[index2,"Profit/Loss (£)"] = round(df_func.loc[index2,"Profit/Loss (£)"] - loss,2)
                    break 
                
                elif index2 == len(df_func) - 1:
                    # If iteration reaches the end of the dataframe and doesn't exit the position - doesn't hit either Target or StopLoss
                    df_func.loc[index1,"Outcome"] = "Long - Still Open"
                    df_func.loc[index1,"Exit Row"] = np.nan
                    df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,"Initial Money (£)"] + df_func.loc[index1,"Profit/Loss (£)"], 2)
                    
                else:
                    continue
                
        # If Indicator gives a SHORT signal, buy into short and create second iteration through rows to see outcome
        elif row1.Indicator == "Short":
            
            # Set Target and StopLoss Variables
            Target = float(row1['Adj Close'] - 2*row1['ATR_14'])
            StopLoss = float(row1['Adj Close'] + 3*row1['ATR_14'])
            df_func.loc[index1, "Target"] = round(Target,2) 
            df_func.loc[index1, "StopLoss"] = round(StopLoss,2)
            
            # Calculate value you wish to short
            # How much went into margin account from sale of borrowed shares? 
            margin_account_gain = position_size*df_func.loc[index1, "Initial Money (£)"]
            # And how many shares did you borrow?
            nshares_borrowed = margin_account_gain/(row1.High - (row1.High - row1.Low) / 2)
            
            for index2, row2 in df_func.loc[(index1+1):].iterrows():
                if row2.Low < Target:
                    df_func.loc[index1, "Outcome"] = "Short - Win"
                    df_func.loc[index1, "Exit Row"] = index2
                    
                    # Profit is cost to buy equal number of borrowed shares now - money from initial sale when price was higher
                    profit = margin_account_gain - (nshares_borrowed*Target)
                    df_func.loc[index1, "Profit/Loss (£)"] = round(profit,2)
                    df_func.loc[index1, "Final Money (£)"] = round(df_func.loc[index1, "Initial Money (£)"] + profit,2)
                    break
                
                elif row2.High > StopLoss:
                    df_func.loc[index1, "Outcome"] = "Short - Lost"
                    df_func.loc[index1, "Exit Row"] = index2
                    
                    # Loss is cost to buy equal number of borrowed shares now - money from initial sale when price was lower
                    loss = (nshares_borrowed*StopLoss) - margin_account_gain
                    df_func.loc[index1, "Profit/Loss (£)"] = -round(loss,2)
                    df_func.loc[index1, "Final Money (£)"] = df_func.loc[index1, "Initial Money (£)"] - loss
                    break
                    
                elif index2 == len(df_func) - 1:
                    # If iteration reaches the end of the dataframe and doesn't exit the position - doesn't hit either Target or StopLoss
                    df_func.loc[index1, "Outcome"] = "Short - Still Open"
                    df_func.loc[index1, "Exit Row"] = np.nan
                    df_func.loc[index1, "Final Money (£)"] = df_func.loc[index1, "Initial Money (£)"]
                    
                else:
                    continue
            
        else:
            print("Something's wrong, indicator value not 0, 1 or 2")
            break 
        
    return df_func