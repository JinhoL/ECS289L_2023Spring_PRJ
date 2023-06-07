# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 10:19:10 2023

@author: user
"""

import json
import requests
import pandas as pd


def fetch_weather_county_year(startYear, endYear, state, county, lon, lat):   
    
    api_request_url = base_url.format(longitude=lon, latitude=lat, startYear=str(startYear), endYear=str(endYear))
    response = requests.get(url=api_request_url, verify=True, timeout=30.00)

    content = json.loads(response.content.decode('utf-8'))

    
    weather = content['properties']['parameter']

    df = pd.DataFrame(weather)    
    df['state_name'] = state
    df['county_name'] = county
    df['lon'] = lon
    df['lat'] = lat
    
    
    return df


def create_weekly_df(df):
    df1 = df.copy()
    # convert index to datetime format    
    df1.index = pd.to_datetime(df['date'], format='%Y%m%d')
    # use 'M' for monthly, use 'W' for weekly
    df1_weekly = df1.resample('W').agg({'T2M_MAX':'mean',
                                       'T2M_MIN':'mean',
                                       'PRECTOTCORR':'sum',
                                       'GWETROOT':'mean',
                                       'EVPTRNS':'mean',
                                       'ALLSKY_SFC_PAR_TOT':'sum'})    
    

    # convert index back to string format YYYYMM
    df1_weekly.index = df1_weekly.index.strftime('%Y%m%d')
    
    return df1_weekly


weather_params = ['T2M_MAX','T2M_MIN', 'PRECTOTCORR', 'GWETROOT', 'EVPTRNS', 'ALLSKY_SFC_PAR_TOT']
base_url = r"https://power.larc.nasa.gov/api/temporal/daily/point?"
base_url += 'parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT,EVPTRNS,ALLSKY_SFC_PAR_TOT&'
base_url += 'community=RE&longitude={longitude}&latitude={latitude}&start={startYear}0915&end={endYear}0715&format=JSON'


# Fetch each county weather data
coordinateDf = pd.read_csv("D:\\Grad\\Food_Security\\Assignment3\\SUMNER_LON_LAT.csv")
df_lon_lat = pd.DataFrame()
print(coordinateDf)


for index, row in coordinateDf.iterrows():
    
    # Access the values of each column in the current row
    stateName = row['state_name']
    countyName = row['county_name']
    lon = row['lon']
    lat = row['lat']

    # Retrieve Weather data from NASA POWER
    df_2003_2022 = pd.DataFrame()
    for year in range(2002, 2022):
        df = fetch_weather_county_year(year, year + 1, stateName, countyName, lon, lat)
    

        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)

        
        df_w = create_weekly_df(df)
        #print("\n=================Weekly data========================\n")
        
        df_2003_2022 = pd.concat([df_2003_2022, df_w])
        df_2003_2022['state_name'] = stateName
        df_2003_2022['county_name'] = countyName
        df_2003_2022['lon'] = lon
        df_2003_2022['lat'] = lat
        
        

    df_lon_lat = pd.concat([df_lon_lat, df_2003_2022])
    print(df_lon_lat.tail())


df_lon_lat.to_csv("D:\\Grad\\Food_Security\\Assignment3\\sumner_weather.csv")
