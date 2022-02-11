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

def long_only_plus_fees(df_func, position_size, pot_size, transaction_fee, stamp_duty):
    
    # Deal with Long and Short separately.
    # Start with a pot of £1000 and only investing 2% of your portfolio
    # Assume entry and midpoint = High - [(High-Low)/2]
    
    # position_size = percentage of capital you wish to invest in each position - e.g. 0.02 = 2%
    # pot_size = starting capital (£) 
    # transaction_fee = cost of each transaction 
    # stamp_duty = stamp duty due with some FTSE100 companies?
    
    for index1, row1 in df_func.iterrows():
        
        if index1 == 0:
            df_func.loc[index1, "Initial Money (£)"] = round(pot_size, 2)
        
        else:
            df_func.loc[index1, "Initial Money (£)"] = round(df_func.loc[(index1-1), "Final Money (£)"], 2)
        
        # If no indicator signal, pass to next row
        if row1.Indicator == "-":
            df_func.loc[index1, "Final Money (£)"] = round(df_func.loc[index1, "Initial Money (£)"], 2)
            continue
        
        # If Indicator gives a LONG signal, buy into long and create second iteration through rows to see outcome
        elif row1.Indicator == "Long":
            
            # Set Target and StopLoss Variables
            Target = float(row1['Adj Close'] + 2*row1['ATR_14'])
            StopLoss = float(row1['Adj Close'] - 3*row1['ATR_14'])
            df_func.loc[index1, "Target"] = round(Target,2)
            df_func.loc[index1, "StopLoss"] = round(StopLoss,2)
            
            # Calculate money spent on the position and nshares bought
            money_spent = position_size*df_func.loc[index1, "Initial Money (£)"]
            nshares_purchased = money_spent/(row1.High - (row1.High - row1.Low) / 2)
            
            for index2, row2 in df_func.loc[(index1+1):].iterrows():
                if row2.High > Target:
                    df_func.loc[index1, "Outcome"] = "Long - Win"
                    df_func.loc[index1, "Exit Row"] = row2.name
                    
                    profit = nshares_purchased*Target - 2*transaction_fee
                    df_func.loc[index1, "Profit/Loss (£)"] = round(profit,2)
                    df_func.loc[index1, "Final Money (£)"] = round(df_func.loc[index1, "Initial Money (£)"] + profit,2)
                    break 
                    
                elif row2.Low < StopLoss:
                    df_func.loc[index1, "Outcome"] = "Long - Lost"
                    df_func.loc[index1, "Exit Row"] = row2.name
                    
                    loss = nshares_purchased*StopLoss + 2*transaction_fee
                    df_func.loc[index1, "Profit/Loss (£)"] = -round(loss,2)
                    df_func.loc[index1, "Final Money (£)"] = round(df_func.loc[index1, "Initial Money (£)"] - loss,2)
                    break 
                
                elif index2 == len(df_func) - 1:
                    # If iteration reaches the end of the dataframe and doesn't exit the position - doesn't hit either Target or StopLoss
                    df_func.loc[index1, "Outcome"] = "Long - Still Open"
                    df_func.loc[index1, "Exit Row"] = np.nan
                    df_func.loc[index1, "Final Money (£)"] = df_func.loc[index1, "Initial Money (£)"]
                    
                else:
                    continue
                
        # If Indicator gives a SHORT signal, buy into short and create second iteration through rows to see outcome
        elif row1.Indicator == "Short":
            continue
            
        else:
            print("Something's wrong, indicator value not 0, 1 or 2")
            break 
        
    return df_func