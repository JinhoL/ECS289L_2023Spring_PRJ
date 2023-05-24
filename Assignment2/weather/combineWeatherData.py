# -*- coding: utf-8 -*-
"""
Created on Wed May 17 19:16:47 2023

@author: user
"""

import csv
import pandas as pd


def createMetFileFromDataFrame(metDf, filePath, latitude, longitude):
    metDf = insertUnitRowForMetFile(metDf)
    
    metDf.to_csv(filePath, sep='\t', index=False, float_format='%.1f', header=True)
    
    addCoordinateInMetFile(filePath, latitude, longitude)
    
    
def insertUnitRowForMetFile(metDf):
    unitRow = ['()', '()', '(MJ^m2)', '(oC)', '(oC)', '(mm)']
    metDf = pd.DataFrame([unitRow], columns=metDf.columns).append(metDf)
    
    print("======  Met File Data ===========")
    print(metDf)
    
    return metDf


def addCoordinateInMetFile(filePath, latitude, longitude):
    existing_rows = []
    new_rows = [
        ['Latitude=' + str(latitude)],
        ['Longitude=' + str(longitude)], 
        []
    ]
    
    with open(filePath, 'r') as file:
        reader = csv.reader(file)
        existing_rows = [row for row in reader]
    

    all_rows = new_rows + existing_rows
    
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(all_rows)


workingDir = "D:\\Grad\\Food_Security\\Assignment2\\"

rcp = "Rcp85"
pastWeatherDir = "weather_2023-05-17_19-51-36\\"
pastWeatherFile = "19.0-105.0.nasapower.csv"
futureWeatherFile = "future_weather_CCSM_" + rcp + ".csv"


dfPast = pd.read_csv(workingDir + pastWeatherDir + pastWeatherFile)
dfFuture = pd.read_csv(workingDir + futureWeatherFile)

dfPast = dfPast.drop('lon', axis=1)
dfPast = dfPast.drop('lat', axis=1)

dfCombine = pd.concat([dfPast, dfFuture])
print(dfCombine.tail(10))


filename = 'Climate_Rcp85_lat19_lon105.met'
createMetFileFromDataFrame(dfCombine, filename, 19, 105)




