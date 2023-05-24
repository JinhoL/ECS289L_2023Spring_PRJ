# -*- coding: utf-8 -*-
"""
Created on Wed May 17 06:17:20 2023

@author: user
"""

import csv
import pandas as pd




def createDataFrame(variable, rcp, coordinate):
    # tasmax
    df = pd.DataFrame()
    dataList = readFile(variable, rcp, coordinate)
    df.index = pd.to_datetime(dataList[0])
    
    
    df['bottom_left'] = dataList[1]
    df['bottom_left'] = df['bottom_left'].astype(float)
    
    df['bottom_right'] = dataList[2]
    df['bottom_right'] = df['bottom_right'].astype(float)

# Use it only if data has 4 lines
# =============================================================================
#     df['top_left'] = dataList[3]
#     df['top_left'] = df['top_left'].astype(float)
#     
#     df['top_right'] = dataList[4]
#     df['top_right'] = df['top_right'].astype(float)
# =============================================================================
    
    if variable == "tasmax" or variable == "tasmin":
        df['average'] = df.mean(axis=1) - 273.15
    elif variable == "rsds":
        df['average'] = df.mean(axis=1) * (60 * 60 * 24) / 1000000
    else:
        df['average'] = df.mean(axis=1)
    
    
    df = df.drop('bottom_left', axis=1)
    df = df.drop('bottom_right', axis=1)
    
# Use it only if data has 4 lines
# =============================================================================
#     df = df.drop('top_left', axis=1)
#     df = df.drop('top_right', axis=1)
# =============================================================================
    
    return df


def readFile(variable, rcp, coordinate):
    dataList = [[] for _ in range(5)]
    yearRanges = ["2023_2043", "2044_2064", "2065_2085", "2086_2100"]
    
    # Concatenate max temperature files
    for i in range(4):
        file_path = "D:\\Grad\\Food_Security\\Assignment2\\CCSM\\" + rcp + "\\" + variable + "\\" + variable + "_all_" + yearRanges[i] + "_" + rcp + coordinate + "\\" + variable + "_all_" + yearRanges[i] + "_" + rcp + coordinate + ".txt"

        with open(file_path, "r") as file:
            
            ind = 0
            for line in file:
                data = line.split(",")
                data.pop(0)
                data.pop(0)
                data.pop(-1)
                
                dataList[ind].extend(data)
                
                ind += 1

    return dataList


def addDateInfo(df, index_list):
    df['Date'] = index_list
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

    df['year'] = pd.to_datetime(df['Date']).dt.year.astype(int)
    df['month'] = pd.to_datetime(df['Date']).dt.month.astype(int)
    df['day'] = pd.to_datetime(df['Date']).dt.dayofyear.astype(int)
    
    return df


def uniformValuesForEachMonth(variable, df, metDf):
    values = df.loc[:, variable].tolist()
    metDf[variable] = [0.0] * len(metDf)


    currMonth = 1
    valueInd = 0

    for index, row in metDf.iterrows():
        if currMonth != row["month"]:
            valueInd += 1
            currMonth += 1
            
            if(currMonth > 12):
                currMonth = 1
        
        if variable == "rain":
            metDf.at[index, variable] = values[valueInd] / 30
        else:
            metDf.at[index, variable] = values[valueInd]

    return metDf
    

def createCsvFileFromDataFrame(metDf, filePath, latitude, longitude):
    metDf = dropRedundantColsForMetFile(metDf)
    print("======  Processed CCSM Data  ===========")
    print(metDf)
    
    metDf.to_csv(filePath, index=False)
    


def dropRedundantColsForMetFile(metDf):
    metDf = metDf.drop('Date', axis=1)
    metDf = metDf.drop('month', axis=1)
    
    return metDf



###############  Create Monthly DataFrame #####################
variables = ["tasmax", "tasmin", "ppt", "rsds"]
rcp = "rcp85"
coordinate = "108.5_109.5_18.5_19.5"

df = pd.DataFrame()
tasmaxDf = createDataFrame(variables[0], rcp, coordinate)
tasminDf = createDataFrame(variables[1], rcp, coordinate)
rainDf = createDataFrame(variables[2], rcp, coordinate)
radn = createDataFrame(variables[3], rcp, coordinate)

df.index = tasminDf.index.tolist()
df['maxt'] = tasmaxDf.loc[:, 'average'].tolist()
df['mint'] = tasminDf.loc[:, 'average'].tolist()
df['rain'] = rainDf.loc[:, 'average'].tolist()
df['radn'] = radn.loc[:, 'average'].tolist()

index_list = df.index.tolist()
df = addDateInfo(df, index_list)
df = df.drop('Date', axis=1)

print("======  Original CCSM Data ===========")
print(df)


###############  Create Met File  ########################
filename = 'future_weather_CCSM_Rcp85.csv'
start_date = '2023-01-01'
end_date = '2100-12-31'

date_range = pd.date_range(start=start_date, end=end_date)
date_list = date_range.strftime('%Y-%m-%d').tolist()

metDf = pd.DataFrame()
metDf = addDateInfo(metDf, date_list)

metDf = uniformValuesForEachMonth('radn', df, metDf)
metDf = uniformValuesForEachMonth('maxt', df, metDf)
metDf = uniformValuesForEachMonth('mint', df, metDf)
metDf = uniformValuesForEachMonth('rain', df, metDf)


createCsvFileFromDataFrame(metDf, filename, 19, 105)




