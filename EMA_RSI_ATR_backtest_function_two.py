# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 17:38:50 2022

@author: cns

Iterates over the dataframe
- where potential signal is triggered, uses exit row value to calculate profit/loss 
- multiple trades can exit on the same row, so need to be careful to add to value / not overwrite if already exists. 

# Variables 
df_func, dataframe with data in it
transaction_fee, fee of a transaction
stamp_duty, stamp duty tax associated with some FTSE100 companies
"""

def backtest_step_two(df_func, pot_size, position_size, transaction_fee, stamp_duty):
    
    import numpy as np
    import pandas as pd
    
    for index1, row1 in df_func.iterrows():
        
        # Use first row as a chance to create the required columns
        if index1 == 0:
            df_func.loc[index1,"Outcome"] = None
            df_func.loc[index1,"Initial Money (£)"] = round(pot_size,2)
            
            df_func["N_shares_purchased"] = 0
            df_func["Purchase_total_inc_fees"] = 0
            
            df_func["N_shares_sold"] = 0
            df_func["Sales_total_inc_fees"] = 0
            df_func["Profit/Loss on Sales (£)"] = 0
            
            df_func["Row Balance (£)"] = 0
            df_func.loc[index1,"Final Money (£)"] = round(pot_size,2)
            continue
        # If not first row, initial money is same as previous rows final money
        else:
            df_func.loc[index1,"Initial Money (£)"] = round(df_func.loc[(index1-1),"Final Money (£)"],2)
        
        # LONG POSITION
        if (row1.Bought == "Bought") and (row1.Entry == "Long"):
            
            # CALCULATES MONEY FROM PURCHASE IN CURRENT ROW
            nshares_purchased = position_size*df_func.loc[index1,"Initial Money (£)"] / df_func.loc[index1,"Open"]
            if nshares_purchased < 1: nshares_purchased = 1
            elif nshares_purchased > 1: nshares_purchased = np.floor(nshares_purchased)
            
            df_func.loc[index1,"N_shares_purchased"] = nshares_purchased
            df_func.loc[index1,"Purchase_total_inc_fees"] = round(nshares_purchased*df_func.loc[index1,"Open"] + transaction_fee,2)

            # CALCULATES SUMMATIONS OF MONEY FOR CURRENT ROW
            df_func.loc[index1,"Row Balance (£)"] = round(df_func.loc[index1,"Sales_total_inc_fees"] - df_func.loc[index1,"Purchase_total_inc_fees"],2)
            df_func.loc[index1,"Final Money (£)"] = round(df_func.loc[index1,'Initial Money (£)'] + df_func.loc[index1,"Row Balance (£)"],2)
                
            # CALCULATES FUTURE MONEY FROM SALES, ADDS VALUES TO EXIT ROW
            exit_row_index = row1['Exit Row']
            
            # IF ITS A WIN
            if df_func.loc[exit_row_index,'High'] > row1.Target:
                
                df_func.loc[index1,"Outcome"] = "Win"
                sales_total_inc_fees = nshares_purchased*row1.Target - transaction_fee
                profit = nshares_purchased*(row1.Target - row1.Open) - transaction_fee
                
                if pd.isnull(df_func.loc[exit_row_index,"N_shares_sold"]):
                    df_func.loc[exit_row_index,"N_shares_sold"] = nshares_purchased
                    df_func.loc[exit_row_index,"Sales_total_inc_fees"] = round(sales_total_inc_fees,2)
                    df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] = round(profit,2)
                elif pd.notnull(df_func.loc[exit_row_index,"N_shares_sold"]):
                    df_func.loc[exit_row_index,"N_shares_sold"] = nshares_purchased + df_func.loc[exit_row_index,"N_shares_sold"]
                    df_func.loc[exit_row_index,"Sales_total_inc_fees"] = df_func.loc[exit_row_index,"Sales_total_inc_fees"] + round(sales_total_inc_fees,2)
                    df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] = df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] + round(profit,2)
                continue 
            # IF ITS A LOSS
            elif df_func.loc[exit_row_index, 'Low'] < row1.StopLoss:
                
                df_func.loc[index1,"Outcome"] = "Loss"
                sales_total_inc_fees = nshares_purchased*row1.StopLoss - transaction_fee
                loss = nshares_purchased*(row1.Open - row1.StopLoss) + transaction_fee

                if pd.isnull(df_func.loc[exit_row_index,"N_shares_sold"]):
                    df_func.loc[exit_row_index,"N_shares_sold"] = nshares_purchased
                    df_func.loc[exit_row_index,"Sales_total_inc_fees"] = round(sales_total_inc_fees,2)
                    df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] = -(round(loss,2))
                elif pd.notnull(df_func.loc[exit_row_index,"N_shares_sold"]):
                    df_func.loc[exit_row_index,"N_shares_sold"] = nshares_purchased + df_func.loc[exit_row_index,"N_shares_sold"]
                    df_func.loc[exit_row_index,"Sales_total_inc_fees"] = df_func.loc[exit_row_index,"Sales_total_inc_fees"] + round(sales_total_inc_fees,2)
                    df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] = df_func.loc[exit_row_index,"Profit/Loss on Sales (£)"] - round(loss,2)
                continue 
            # IF POSITION IS STILL OPEN
            else:
                df_func.loc[index1,"Outcome"] = "Still Open"

        # SHORT POSITION
        # TODO - Add in code for short position
        # if (row1.Bought == "Bought") and (row1.Entry == "Long"):
            
        # IF NO BOUGHT SIGNAL, CALCULATES SUMMATION OF CURRENT ROW
        elif pd.isnull(df_func.loc[index1,"Bought"]):
            df_func.loc[index1,"Row Balance (£)"] = df_func.loc[index1,"Sales_total_inc_fees"] - df_func.loc[index1,"Purchase_total_inc_fees"]
            df_func.loc[index1,"Final Money (£)"] = df_func.loc[index1,'Initial Money (£)'] + df_func.loc[index1,"Row Balance (£)"]
            continue
            
    return df_func