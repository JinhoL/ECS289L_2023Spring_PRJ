import json
import subprocess
import rasterio
from pyproj import Transformer
import datetime


# ============================================================================================================================================
# first, examining the structure of the files I downloaded
dir_main = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/output/ML-ARCHIVES--v01/CROPSCAPE/DATA-DOWNLOADS/'

# following the structure of the directory name and file from downloaded zip files, which are organized by year
def pathname_for_year(year):
    last_dir_name = f'{str(year)}_30m_cdls/'
    file_name = f'{str(year)}_30m_cdls.tif'
    return dir_main + last_dir_name + file_name

# test
print(pathname_for_year(2021))
# ============================================================================================================================================

# ============================================================================================================================================
def pull_useful(ginfo):  # should give as input the result.stdout from calling gdalinfo -json
    useful = {}
    useful['band_count'] = len(ginfo['bands'])
    useful['cornerCoordinates'] = ginfo['cornerCoordinates']
    useful['proj:transform'] = ginfo['stac']['proj:transform']
    useful['size'] = ginfo['size']
    useful['bbox'] = ginfo['stac']['proj:projjson']['bbox']
    useful['espgEncoding'] = ginfo['stac']['proj:epsg']
    return useful

path_to_file = pathname_for_year(2012)

gdalInfoReq = " ".join(["gdalinfo", "-json", path_to_file])
print(gdalInfoReq)
#print(gdalInfoReq[k])
result = subprocess.run([gdalInfoReq], shell=True, capture_output=True, text=True)

#print(result)
#print(result.stdout)
print()
gdalInfo = json.loads(result.stdout)

#useful = pull_useful(gdalInfo)
#print(json.dumps(useful, indent=2, sort_keys=True))
# ============================================================================================================================================

# ============================================================================================================================================
# Function to transform from EPSG:4326 to EPSG:5070.  The rasterio-based function we use below will take coordinates in EPSG:5070, since the tif files we are using here are in EPSG:5070.
transformer = Transformer.from_crs('EPSG:4326', 'EPSG:5070')

def from_4326_to_5070(lon,lat):
    # I'm not sure why the role positions of lon-lat are different on input and output
    # but that is what my numerous small test runs showed to me
    new_lon,new_lat = transformer.transform(lat,lon)
    return new_lon, new_lat

# test on coordinates from central Kensas
old_lat = 37.2 # Center Lot of Kensas - Sumner
old_lon = -97.4 # Center LAT of Kensas - Sumner
print(from_4326_to_5070(old_lon,old_lat))
# (you can check this at https://epsg.io/transform)
# ============================================================================================================================================


### ================================================================
# Function that fetches a 3x3 square of pixel values from the given tif file.  The pixels in the tif file correspond to  30m x 30m, so we are looking at a rouhgly 100m x 100m area that is all or mostly soybean field 
# Note that in 2008 the target area was planted mainly with maize, but in 2022 it was planted with soybeans
### ================================================================
# expects lon-lat to be in EPSG:4326.  
# These are converted to EPSG:5070 inside the function
def get_coordinate_pixels(tiff_file, lon, lat):
    dataset = rasterio.open(tiff_file)
    lon_new,lat_new = from_4326_to_5070(lon,lat)
    # print(lon_new,lat_new)
    py, px = dataset.index(lon_new, lat_new)
    # print(py, px)
    # create 3px x 3px window centered on the lon-lat
    window = rasterio.windows.Window(px-1, py-1, 3, 3)
    clip = dataset.read(window=window)
    return clip

'''    
# test
old_lat = 36.9 # Somewhere Lot of Kensas
old_lon = -97.9 # Somewhere Lat of Kensas

path_to_file = pathname_for_year(2008)
print(get_coordinate_pixels(path_to_file,old_lon,old_lat))
print()
path_to_file = pathname_for_year(2021)
print(get_coordinate_pixels(path_to_file,old_lon,old_lat))

# 2022 Kansas Cropland Data Layer | USDA NASS
# https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_ks22.htm
# Winter Wheat 24
old_lat = 36.9
old_lon = -97.9
[[[24 24 24]
  [24 24 24]
  [24 24 24]]]

[[[1 1 1]
  [1 1 1]
  [1 1 1]]]
'''

# ============================================================================================================================================
# land_use_val should be an integer; see, e.g., 
#     https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_ia22.htm
#     for mapping from values to meanings
def usage_is_here(year, lon, lat, land_use_val):
    path_to_file = pathname_for_year(year)
    arr = get_coordinate_pixels(path_to_file, lon, lat)
    out = True
    for i in range(0,3):
        for j in range(0,3):
            out = out & (arr[0][i][j] == land_use_val)
    return out

def WinterWheat_is_here(year, lon, lat):
    return usage_is_here(year,lon,lat,24)
'''
old_lat = 36.9
old_lon = -97.9
print(WinterWheat_is_here(2008, old_lon, old_lat))
print(WinterWheat_is_here(2021, old_lon, old_lat))
'''

### ================================================================
# Importing the dictionary with lon-lat sequences.  Also setting a second dict that will hold lists lon-lats that are in winterWheat fields.
### ================================================================

archive_dir = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/output/ML-ARCHIVES--v01/'
in_file = 'state_county__seq_of_lon_lats.json'

f = open(archive_dir + in_file)
dict = json.load(f)

print(dict.keys())

### ================================================================
# Function that scans through one list of lon-lats and finds first set that are in winterWheat fields
### ================================================================
def gen_WinterWheat_lon_lats(year, state, county, count):
    list = dict[state][county]
    i = 0
    out_list = []
    for ll in list:
        if WinterWheat_is_here(year, ll[0], ll[1]):
            out_list += [ll]
            i += 1
        if i == count:
            return out_list, []
    print(f'\nFor {str(year)}, {state}, {county}: \nFailed to find {str(count)} lon-lats that were in white wheat fields. Found only {str(i)}.\n')
    short_fall_record = [year, state, county, i]
    return out_list, short_fall_record

list, short = gen_WinterWheat_lon_lats(2008, 'KANSAS', 'WYANDOTTE', 20)
print(list)
print(short)
print()

### ================================================================
# Function that generates a fixed number of lon-lats in Winter Wheat fields for each year and each county. This took quite a while to run completely -- about 4 hours.
### ================================================================
working_dir = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/OUTPUT-v01/'
dict1_file = 'year_state_county_winterwheat_seq.json'
short_list = 'year_state_county_shortfalls.json'

def gen_all_WinterWheat_lists(dict, count):
    dict1 = {}
    for year in range(2008,2023):
        dict1[year] = {}
        for key in dict.keys():
            dict1[year][key] = {}    
    print(dict1.keys())    
    
    shortfall_list = []

    i = 0
    for year in dict1.keys():
        print('\tYear:', year)
        state = 'KANSAS'
        for county in dict[state].keys():
            list, short = gen_WinterWheat_lon_lats(year, state, county, count)
            dict1[year][state][county] = list
            if short != []:
                shortfall_list += [short]
                            
            i += 1
            if i % 20 == 0:
                print(f'Have generated WinterWheat lon-lat lists for {str(i)} year-county pairs')
            if i % 50 == 0:
                with open(working_dir + dict1_file, 'w') as fp:
                    json.dump(dict1, fp)
                with open(working_dir + short_list, 'w') as fp:
                    json.dump(shortfall_list, fp)
                
    return dict1, shortfall_list
                    
print(datetime.datetime.now())
dict1, short = gen_all_WinterWheat_lists(dict, 2)
print(datetime.datetime.now())

# ==================================================================
archive_dir = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/output/ML-ARCHIVES--v01/'
dict1_file = 'year_state_county_winterwheat_seq.json'
short_list = 'year_state_county_shortfalls.json'

with open(archive_dir + dict1_file, 'w') as fp:
    json.dump(dict1, fp)
with open(archive_dir + short_list, 'w') as fp:
    json.dump(short, fp)

zero_falls = []

for l in short:
    if l[3] == 0:
        zero_falls += [[l]]
        
print(len(zero_falls))

print(json.dumps(zero_falls,indent=4))

archive_dir = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/output/ML-ARCHIVES--v01/'
zero_file = 'year_state_county_whitewheat_zero_falls.json'
with open(archive_dir + zero_file, 'w') as fp:
    json.dump(zero_falls, fp)

import pandas as pd

archive_dir = '/Users/jinholee/Desktop_local/2023_Spring_FoodSecurity/HW3/output/ML-ARCHIVES--v01/'
yscy_file = 'year_state_county_yield.csv'

df_yscy = pd.read_csv(archive_dir + yscy_file)
print('Top of df_yscy')
print(df_yscy.head())

zero_with_yield = []
for l in zero_falls:
    year = l[0][0]
    state = l[0][1]
    county = l[0][2]
    rows = df_yscy[(df_yscy['year'] == year) & \
                  (df_yscy['state_name'] == state) & \
                  (df_yscy['county_name'] == county)]
    if len(rows) > 0:
        y = rows['yield'].iloc[0]
        zero_with_yield += [{'year':year, 'state_name':state, \
                             'county_name':county, 'yield':y}]

print('\nLength of zero_with_yield is: ', len(zero_with_yield))
print('\nListing of zero_with_yield')
df_zwy = pd.DataFrame(zero_with_yield)
print(df_zwy.head(30))
    
zero_with_yield = 'year_state_county_winterWheat_zero_with_yield.csv'
df_zwy.to_csv(archive_dir + zero_with_yield, index=False)
