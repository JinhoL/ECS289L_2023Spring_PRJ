# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:17:38 2023

@author: user
"""


import sys
import os
import numpy as np
import datetime

sys.path.append(r"D:\Bestiapop\bestiapop-master\\bestiapop")
from bestiapop import bestiapop as bp


def curr_timestamp():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_datetime


# Create a folder
working_dir = 'D:\\Grad\\Food_Security\\Assignment2\\'

target_dir = 'weather_' + curr_timestamp()
output_path = working_dir + target_dir
print('Output files will be written into: ', output_path, '\n')

os.mkdir(working_dir + target_dir)



# Setup the parameters
year_range = '2011-2022'

# these are the only climate variables supported by BestiaPop on NASAPOWER data
climate_variables = np.array(['daily_rain', 'max_temp', 'min_temp', 'radiation'])

# on NASAPOWER, it works on round numbers and xx.5 numbers only; 
# if you give it a coordinate such as 145.63 it will round to 145.5 and/or 146
lat_range = [19, 19.5] 
lon_range = [105, 105.5] 


action = 'generate-climate-file'
data_source = 'nasapower'
output_type = 'csv'

print('Fetching data for {}/{}'.format(lat_range, lon_range))

climate_data = bp.CLIMATEBEAST(
        action=action,
        data_source=data_source,
        output_path=output_path,
        output_type=output_type,
        input_path=None,
        climate_variables=climate_variables,
        year_range=year_range,
        lat_range=lat_range,
        lon_range=lon_range,
        multiprocessing=None
        )
print()
print('The climate_data object has value:\n', str(climate_data))
print('\n\nThe fields with the climate_data object are:\n\n', climate_data.__dir__())
print()
print('invoking climate_data.process_records(action)\n')
climate_data.process_records(action)
print('\nfinished with invocation of climate_data.process_records(action)\n\n')
print('The list of files created is as follows:\n')

# Print downloaded files
for root, dirs, files in os.walk(output_path):
    for file in files:
        # print the file name
        print(os.path.join(root, file))







