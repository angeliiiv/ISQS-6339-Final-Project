# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 10:40:01 2022

@author: angel
"""

import pandas as pd
avg_annual_earnings = pd.read_excel('national_weekly_incomev2.xlsx')
#importing the data into a dataframe
aae = avg_annual_earnings[['Year','Period','Value']]
aae['Annual Earnings'] = aae['Value']*52 # we are assuming a 52 year work week for the conversion of weekly earnings to a annual salary

# here we are cleaning the data and getting it ready for merging by making sure it is in a quarterly format
aae['Quarter'] = 'Q1'
aae.loc[aae['Period'] == 'Q02' , 'Quarter'] = 'Q2'
aae.loc[aae['Period'] == 'Q03' , 'Quarter'] = 'Q3'
aae.loc[aae['Period'] == 'Q04' , 'Quarter'] = 'Q4'

aae['Date'] = aae['Year'].astype(str) + aae['Quarter'].astype(str)

#droppping the columns we don't need
aae = aae.drop(['Value','Period','Quarter','Year'],axis=1)
#
aae = aae.set_index('Date')




""" Robert """
fedfile = 'federal_reserve_data.csv'


##### Convert the separate date columns into one datetime column and make it the index
fedres = pd.read_csv(fedfile, parse_dates = {'date' : ['Year', 'Month', 'Day']}, index_col = 'date')

#### Replace all spaces in column names with an underscore
fedres.columns = fedres.columns.str.replace(' ', '_')


#### Make new df that takes the mean values of each quarter for all coulums
fedres1 = fedres.resample('Q').agg({'Federal_Funds_Target_Rate':'mean', 'Federal_Funds_Upper_Target':'mean'
                          , 'Federal_Funds_Lower_Target':'mean', 'Effective_Federal_Funds_Rate':'mean','Real_GDP_(Percent_Change)':'mean'
                          , 'Unemployment_Rate':'mean','Inflation_Rate':'mean'})

fedres1['Date'] = fedres1.index

fedres1['Date'] = fedres1['Date'].dt.to_period('Q')

fed = fedres1.set_index('Date')


""" Monica """ 
cpi = pd.read_csv('quarter_average_sales price.csv')

cpi['DATE']=pd.to_datetime(cpi['DATE'])

for x in cpi:
  cpi['Date']=cpi['DATE'].dt.to_period('Q')  

qasp = cpi

qasp = cpi.drop('DATE',axis=1)
qasp = qasp.set_index('Date')



""" Robert """

cpi_housing_file = 'national_cpi_housing_data.csv'

cpi_df = pd.read_csv(cpi_housing_file, skiprows = 11)

cpi_df = cpi_df.melt(id_vars = 'Year', value_vars = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

      , var_name='Month', value_name = 'CPI')

cpi_df['Date'] = cpi_df['Year'].astype(str) + '-' + cpi_df['Month'].astype(str)
cpi_df['Date'] = pd.to_datetime(cpi_df['Date'])
cpi_df = cpi_df.drop(['Year','Month'],axis=1)
cpi_df = cpi_df.set_index('Date')
cpi_df = cpi_df.resample('Q').agg({'CPI':'mean'})
cpi_df['Date'] = cpi_df.index
cpi_df['Date'] = cpi_df['Date'].dt.to_period('Q')
cpi_df = cpi_df.set_index('Date')


cpi_df.to_csv('cpi_df2.csv')

dffinal = pd.merge(qasp,cpi_df,left_index=True, right_index=True)
dffinal = dffinal.merge(fed,how='inner',left_index=True,right_index=True)
dffinal = dffinal.merge(qasp,how='inner',left_index=True,right_index=True)

dffinal.to_csv('merged_data.csv')
