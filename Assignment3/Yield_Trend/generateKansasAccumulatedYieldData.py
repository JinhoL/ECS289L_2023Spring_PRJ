# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 14:52:13 2023

@author: user
"""


import pandas as pd


weatherDf = pd.read_csv('D:\\Grad\\Food_Security\\Assignment3\\Weather_Soil_Yield_Data.csv')
accumulatedYieldDf = pd.DataFrame()


counties = weatherDf['county_name'].unique().tolist()
print(counties)


for c in counties:
    accumulatedYield = 0
    
    for year in range(2003, 2023):
        yearWeatherDf = weatherDf[(weatherDf['year'] == year) & (weatherDf['county_name'] == c)]
    
        allCountyYield = 0
        for index, row in yearWeatherDf.iterrows():
            allCountyYield += row['yield']
    
    
        accumulatedYield += allCountyYield
        yearWeatherDf['accumulated_yield'] = accumulatedYield
            
        accumulatedYieldDf = pd.concat([accumulatedYieldDf, yearWeatherDf])
    
accumulatedYieldDf.to_csv("D:\\Grad\\Food_Security\\Assignment3\\Yield_Trend_Data.csv", index=False)
