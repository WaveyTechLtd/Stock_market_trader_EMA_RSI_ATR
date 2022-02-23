# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 11:21:38 2022

@author: cns

Iterates over the dataframe, if previous timeblock indicator was long or short, 
- annotates positions and hypothetical exit rows of long and short trades where those values are meet

# Variables 
df_func, dataframe with data in it
transaction_fee, fee of a transaction
stamp_duty, stamp duty tax associated with some FTSE100 companies
"""
def backtest_step_one(df_func, max_positions):
    
    import numpy as np
    import pandas as pd
    
    # Deal with Long and Short separately.
    # Start with a pot of £1000 and only investing 2% of your portfolio
    # Assume entry and midpoint = High - [(High-Low)/2]
    
    # position_size = percentage of capital you wish to invest in each position - e.g. 0.02 = 2%
    # pot_size = starting capital (£) 
    # transaction_fee = cost of each transaction 
    # stamp_duty = stamp duty due with some FTSE100 companies?

    # First cycle identifies the target, stoploss, exit row and transaction fees of a trade 
    for index1, row1 in df_func.iterrows():
        
        if index1 == 0:
            continue
        
        elif (df_func.loc[(index1-1),"Indicator"] == "Long"):
            
            # Set entry type descriptor
            df_func.loc[index1,"Entry"] = "Long"
            
            # Set Target and StopLoss Variables, based on Open price of subsequent time block.
            # Cannot yet calculate ATR value for this time block, so use preceding row1.ATR_14 value
            Target = float(df_func.loc[index1,"Open"] + 2*df_func.loc[(index1-1),'ATR_14'])
            df_func.loc[index1,"Target"] = round(Target,2)
            StopLoss = float(df_func.loc[index1,"Open"] - 3*df_func.loc[(index1-1),'ATR_14'])
            df_func.loc[index1,"StopLoss"] = round(StopLoss,2)
            
            # Calculate Trade exit row
            for index2, row2 in df_func.loc[index1:].iterrows():
                
                if row2.High > Target:
                    df_func.loc[index1,"Exit Row"] = row2.name
                    break 
                    
                elif row2.Low < StopLoss:
                    df_func.loc[index1,"Exit Row"] = row2.name
                    break 
                
                elif index2 == len(df_func) - 1:
                    df_func.loc[index1,"Exit Row"] = np.nan
                
                else:
                    continue
                
        # If Indicator gives a SHORT signal, buy into short and create second iteration through rows to see outcome
        elif df_func.loc[(index1-1),"Indicator"] == "Short":
            
            # Set entry type descriptor
            df_func.loc[index1,"Entry_type"] = "Short"
            
            # Set Target and StopLoss Variables, based on Open price of subsequent time block.
            # Cannot yet calculate ATR value for this time block, so use preceding row1.ATR_14 value
            Target = float(row1['Adj Close'] - 2*df_func.loc[(index1-1),'ATR_14'])
            df_func.loc[index1, "Target"] = round(Target,2) 
            StopLoss = float(row1['Adj Close'] + 3*df_func.loc[(index1-1),'ATR_14'])
            df_func.loc[index1, "StopLoss"] = round(StopLoss,2)
            
            # Calculate Trade exit row
            for index2, row2 in df_func.loc[index1:].iterrows():
                
                if row2.Low < Target:
                    df_func.loc[index1,"Exit Row"] = row2.name
                    break 
                    
                elif row2.High > StopLoss:
                    df_func.loc[index1,"Exit Row"] = row2.name
                    break 
                
                elif index2 == len(df_func) - 1:
                    df_func.loc[index1,"Exit Row"] = np.nan
                
                else:
                    continue  
        
    # custom function for removing elements from a list
    def remove_values_from_list(the_list, val):
        return [value for value in the_list if value != val]

    # Create an empty list, which will store exit rows of trades
    # Can use length of this list, as well as value of first element, to limit total number of trades
    position_exit_list = []    
    
    for index1, row1 in df_func.iterrows():
        
        # If have reached the row after an exit row for trades, remove prior row as they'd have been sold
        if (index1-1) in position_exit_list:
            position_exit_list = remove_values_from_list(position_exit_list, (index1-1))
            
        if pd.notnull(row1.Entry):
            if len(position_exit_list) >= max_positions:
                continue
            elif len(position_exit_list) < max_positions:
                position_exit_list.append(df_func.loc[index1,"Exit Row"])
                df_func.loc[index1,"Bought"] = "Bought"
                continue
        else:
            continue

    return df_func