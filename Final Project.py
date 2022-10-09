# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 10:40:01 2022

@author: angel
"""

import pandas as pd


#enter the filepath to your flder that contains the CSV files below
input_filepath = "C:\\Users\\angel\\OneDrive\\Documents\\TTU Masters Program\\ISQS-6339\\Final Project\\Proposal Datasets\\"

#enter the output filepath where you woud like the final file to be
output_filepath = "C:\\Users\\angel\\OneDrive\\Documents\\TTU Masters Program\\ISQS-6339\\Final Project\\Proposal Datasets\\"

""" Average Earnings - Manipulation """
# reading in the CSV file
avg_annual_earnings = pd.read_excel(input_filepath + 'national_weekly_incomev2.xlsx')

#Selecting the columns we need and adjusting the data
aae = avg_annual_earnings[['Year','Period','Value']]
aae['Annual Earnings'] = aae['Value']*52 # we are assuming a 52 year work week for the conversion of weekly earnings to a annual salary

# here we are cleaning the data and getting it ready for merging by making sure it is in a quarterly format
aae['Quarter'] = 'Q1'
aae.loc[aae['Period'] == 'Q02' , 'Quarter'] = 'Q2'
aae.loc[aae['Period'] == 'Q03' , 'Quarter'] = 'Q3'
aae.loc[aae['Period'] == 'Q04' , 'Quarter'] = 'Q4'

# concatenating the year and quarter file to get a date column
aae['Date'] = aae['Year'].astype(str) + aae['Quarter'].astype(str)

#droppping the columns we don't need
aae = aae.drop(['Value','Period','Quarter','Year'],axis=1)

# For the sake of the merge we need the date column to be in Datetime and to period so the datatypes will match the other files
aae['Date'] = pd.to_datetime(aae['Date'])
aae['Date'] = aae['Date'].dt.to_period('Q')
aae = aae.set_index('Date')




""" Federal Reserve Dataset - Manipulation """
#bringing in our data
fedfile = 'federal_reserve_data.csv'

#taking current date columns and parsing together to get one date column. Also replacing spaces with underscore in column names
fedres = pd.read_csv(input_filepath + fedfile, parse_dates = {'date' : ['Year', 'Month', 'Day']}, index_col = 'date')
fedres.columns = fedres.columns.str.replace(' ', '_')

#transforming the data to be quarterly versus monthly using mean
fedres1 = fedres.resample('Q').agg({'Federal_Funds_Target_Rate':'mean', 'Federal_Funds_Upper_Target':'mean'
                          , 'Federal_Funds_Lower_Target':'mean', 'Effective_Federal_Funds_Rate':'mean','Real_GDP_(Percent_Change)':'mean'
                          , 'Unemployment_Rate':'mean','Inflation_Rate':'mean'})

#converting date into datetime datatype and formatting similar to other datastes 
fedres1['Date'] = fedres1.index
fedres1['Date'] = fedres1['Date'].dt.to_period('Q')

#dropping unneeded columns and setting index
fed = fedres1.set_index('Date')
fed = fed.drop(['Federal_Funds_Upper_Target','Federal_Funds_Lower_Target','Federal_Funds_Target_Rate'],axis=1)


""" Quarterly Average Home Sales Price - QASP """ 
# bringing in data
qasp = pd.read_csv(input_filepath + 'quarter_average_sales price.csv')

# data was already in a quarterly form so we just need to adjust the date format
qasp['DATE']=pd.to_datetime(qasp['DATE'])
for x in qasp:
  qasp['Date']=qasp['DATE'].dt.to_period('Q')  

#dropping previous date column
qasp = qasp.drop('DATE',axis=1)

#setting index as final step for merge
qasp = qasp.set_index('Date')



""" Housing CPI Data - Manipulation """
# bringing in our data and melting to transform from a wide dataset to a long
cpi_housing_file = 'national_cpi_housing_data.csv'
cpi_df = pd.read_csv(input_filepath + cpi_housing_file, skiprows = 11)
cpi_df = cpi_df.melt(id_vars = 'Year', value_vars = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], var_name='Month', value_name = 'CPI')

#manipualting the year and month columns to get into a quarterly format
cpi_df['Date'] = cpi_df['Year'].astype(str) + '-' + cpi_df['Month'].astype(str)
cpi_df['Date'] = pd.to_datetime(cpi_df['Date'])
cpi_df = cpi_df.drop(['Year','Month'],axis=1)
cpi_df = cpi_df.set_index('Date')

#transforming data from monthly to quarterly using mean
cpi_df = cpi_df.resample('Q').agg({'CPI':'mean'})
cpi_df['Date'] = cpi_df.index
cpi_df['Date'] = cpi_df['Date'].dt.to_period('Q')

#setting index as final step for merge
cpi_df = cpi_df.set_index('Date')


""" Merging our 4 datasets """
dffinal = pd.merge(qasp,cpi_df,left_index=True, right_index=True)
dffinal = dffinal.merge(fed,how='inner',left_index=True,right_index=True)
dffinal = dffinal.merge(aae,how='inner',left_index=True,right_index=True)
dffinal = dffinal.iloc[3:]

""" Cleaning our Data """
# we need to fill in thr real GDP percentage for 2017Q1. We are going to use the mean of . 
dffinal['group_column'] = dffinal.index.map(lambda x: str(x)[4:]) #seperating quarter from the index as our group by base
dffinal['Real_GDP_(Percent_Change)'] = dffinal['Real_GDP_(Percent_Change)'].fillna(dffinal.groupby('group_column')['Real_GDP_(Percent_Change)'].transform('mean'))
dffinal = dffinal.drop('group_column',axis=1)

""" Output to CSV """
dffinal.to_csv(output_filepath + 'merged_data.csv')






