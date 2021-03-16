#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

#----------------
# Read data
#----------------
df = pd.read_csv("ALKOdata.txt", sep = '\t')
df.head()

#----------------
# Assumption
#----------------
leadtime = 3 #3 weeks lead time to replenish the stock once an order has been placed
ship_cost = 100 #per each shipment regardless of shipment size
bean_cost = 6 #the wholesale price they pay for the beans is $6 per pound
holding_cost = 0.2 #the annual unit holding cost
service_level = 0.9 #service level for four current warehouses
Hayward_hold_cost = 0.35 #annual unit holding cost would increase to 35% at this newfacility
obj_service_level = 0.99 #target service level for new warehouse at Hayward


#----------------
# Average Inventory currently maintained at each of the four location
#----------------

# three-week demand calculation
def three_week_demand(df):
    demand_df=[]
    for i in range(len(df)-2):
        demand = df[i] + df[i+1] + df[i+2]
        demand_df.append(demand)
    return(demand_df)

# average inventory calculation
def avg_inventory_cal(df, holding_cost, bean_cost, ship_cost, service_level):
    unit_hold = holding_cost * bean_cost #annual
    avg_yr_demand = df.sum() / 4
    optimal_order_q = np.sqrt(2 * ship_cost * avg_yr_demand / unit_hold)
    ROP = np.quantile(three_week_demand(df), service_level)
    safety_stock = ROP - np.array(three_week_demand(df)).mean()
    Avg_inventory = optimal_order_q/2 + safety_stock
    yr_order_cost = (avg_yr_demand / optimal_order_q) * ship_cost
    yr_hold_cost = Avg_inventory * unit_hold
    stock_list = [optimal_order_q, ROP, safety_stock, Avg_inventory, yr_order_cost, yr_hold_cost]
    return(stock_list)


df_inv = []
for col in df.columns[1:]:
    df_inv.append(avg_inventory_cal(
                      df[col], 
                      holding_cost, 
                      bean_cost, 
                      ship_cost, 
                      service_level))

df_inv = pd.DataFrame(df_inv, 
                      columns=['optimal order quantity', 'ROP', 'safety stock', 
                               'avg inventory', 'annual order cost', 'annual holding cost'], 
                      index=df.columns[1:])

df_inv['annual total cost'] = df_inv['annual order cost'] + df_inv['annual holding cost']
df_inv = df_inv.append(df_inv.agg(['sum']))
df_inv


print(
    f"""On average, ALKO maintains\n {round(float(df_inv.loc['SanMateo','avg inventory']), 2)} inventories at {str(df.columns[1])},\n {round(float(df_inv.loc['Oakland','avg inventory']), 2)} inventories at {str(df.columns[2])},\n {round(float(df_inv.loc['Fremont','avg inventory']), 2)} inventories at {str(df.columns[3])},\nand {round(float(df_inv.loc['Dublin','avg inventory']), 2)} inventories at {str(df.columns[4])}."""
)


#----------------
# Total annual ordering and holding costs across all four locations (excluding cost of materials)
#----------------

print(
    f"""Across all four locations, total annual ordering and holding cost is ${round(float(df_inv.iloc[-1,-1]), 2)}"""
)


#----------------
# Suppose ALKO centralizes the inventories into Hayward. Then, how much inventory would ALKO carry on average, and what would the total annual ordering and holding costs be?
#----------------

df["Hayward"] = df.iloc[:,1:].sum(axis=1)

df_hay = avg_inventory_cal(df["Hayward"],
                           Hayward_hold_cost,
                           bean_cost,
                           ship_cost,
                           obj_service_level)

df_hay = pd.DataFrame(df_hay, 
                      columns = ['Hayward'],
                      index=['optimal order quantity', 'ROP', 'safety stock', 
                               'avg inventory', 'annual order cost', 'annual holding cost'])


df_hay.loc['annual total cost'] = df_hay.loc['annual order cost'] + df_hay.loc['annual holding cost']
df_hay

print(
    f"""If ALKO centralizes the inventories into Hayward, the inventory would be {round(float(df_hay.loc['avg inventory','Hayward']), 2)} on average, and the total annual ordering and holding costs would be ${round(float(df_hay.loc['annual total cost', 'Hayward']), 2)}.""" 
)

#----------------
# Should ALKO centralize? If so, how much would ALKO save? If not, how much would ALKO lose?
#----------------

save_cost = -(df_hay.loc['annual total cost'] - df_inv.iloc[-1, -1])
save_cost


print(
    f"""ALKO should centralize because doing so would help it save ${round(float(save_cost), 2)}.""" 
)



