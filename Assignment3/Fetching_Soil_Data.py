# This useful if I want to give unique names to directories or files
import datetime
import pandas as pd
import urllib.request
import json
import subprocess
import rasterio
import os

class FetchingSoil():
    def __init__(self):
        self.fileFullName = {}
        self.df_scll = None
        self.urlkeys = None

    
    def curr_timestamp(self):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        return formatted_datetime
    
    def read_lonlat(self, archive_dir, scll_filename):
        #archive_dir = '/Users/rick/AG-CODE--v03/ML-ARCHIVES--v01/'
        #scll_filename = 'state_county_lon_lat.csv'

        self.df_scll = pd.read_csv(archive_dir + scll_filename)
        print(self.df_scll.head())
        print()
        print(len(self.df_scll))
    
    def fetch_gaez_data(self, tif_dir, url):
        self.urlkeys = url.keys()
        print(self.urlkeys)

        # Fetch the TIF files using the associated URLs

        curr = self.curr_timestamp()
        

        # fetching the tif files from web and writing into local files
        for k in self.urlkeys:
            self.fileFullName[k] = tif_dir + k + '.tif'
            if os.path.exists(self.fileFullName[k]):
                continue
            print(self.fileFullName[k])
            urllib.request.urlretrieve(url[k], self.fileFullName[k])


    def pull_useful(self, ginfo):  # should give as input the result.stdout from calling gdalinfo -json
        useful = {}
        useful['band_count'] = len(ginfo['bands'])
        # useful['cornerCoordinates'] = ginfo['cornerCoordinates']
        # useful['proj:transform'] = ginfo['stac']['proj:transform']
        useful['size'] = ginfo['size']
        # useful['bbox'] = ginfo['stac']['proj:projjson']['bbox']
        # useful['espgEncoding'] = ginfo['stac']['proj:epsg']
        return useful
    
    def fetch_meta_data(self):
        gdalInfoReq = {}
        gdalInfo = {}

        useful = {}
        for k in self.urlkeys:
            gdalInfoReq[k] = " ".join(["gdalinfo", "-json", self.fileFullName[k]])
            print(gdalInfoReq[k])
            result = subprocess.run([gdalInfoReq[k]], shell=True, capture_output=True, text=True)
            #print(result.stdout)
            gdalInfo[k] = json.loads(result.stdout)
            # if k == 'AEZ_classes':
            #     print(json.dumps(gdalInfo[k], indent=2, sort_keys=True))

            useful[k] = self.pull_useful(gdalInfo[k])
            print('\n', k)
            print(json.dumps(useful[k], indent=2, sort_keys=True))

    # following https://gis.stackexchange.com/a/299791, adapted to fetch just one pixel
    def get_coordinate_pixel(self, tiff_file, lon, lat):
        dataset = rasterio.open(tiff_file)
        py, px = dataset.index(lon, lat)
        # create 1x1px window of the pixel
        window = rasterio.windows.Window(px, py, 1, 1)
        # read rgb values of the window
        clip = dataset.read(window=window)
        # print(clip)
        return clip[0][0][0]

    def pull_pixel_val(self):
        # testing the function
        tiff_file = self.fileFullName['AEZ_classes']
        # tiff_file = '/Users/rick/AG-CODE--v03/GAEZ-SOIL-for-ML/OUTPUTS/2023-05-20_23-09-36__AEZ_classes.tif'
        print(self.df_scll.iloc[[0]])
        test_lon = self.df_scll.iloc[0]['lon']
        test_lat = self.df_scll.iloc[0]['lat']
        print(test_lon, test_lat, type(test_lon), type(test_lat))
        print()

        val = self.get_coordinate_pixel(tiff_file, test_lon, test_lat)
        print(type(val))
        print(val)

    def combine_soil(self):
        df3 = self.df_scll.copy()
        print(df3.head())
        print(len(df3))

        for k in self.urlkeys:
            # df3[k] = df3.apply(lambda r: fetch_tif_value(r['lon'], r['lat'], k, False), axis=1)
            tiff_file = self.fileFullName[k]
            df3[k] = df3.apply(lambda r: self.get_coordinate_pixel(tiff_file, r['lon'], r['lat']), axis=1)

        print()
        print(df3.head())
        print(len(df3))
        self.replace_soil_data(df3)

    def replace_soil_data(self, df3):
        df4 = df3.copy()

        # Get one hot encoding of columns 'AEZ-classes'
        one_hot = pd.get_dummies(df4['AEZ_classes'], dtype=int)
        # Drop original as it is now encoded
        df4 = df4.drop('AEZ_classes', axis=1)
        # Join the encoded df
        df4 = df4.join(one_hot)

        print(len(df4))
        print("df4 head:", df4.head())
        print(df4.columns.tolist())
        # output was ['state_name', 'county_name', 'lon', 'lat', 'nutr_ret_high',
        #             'soil_qual_high', 'soil_qual_low', 'suit_irrig_high_soy',
        #              16, 17, 18, 19, 20, 21, 27, 28, 32]

        print()
        cols = {16: 'AEZ_1',
                17: 'AEZ_2',
                18: 'AEZ_3',
                19: 'AEZ_4',
                20: 'AEZ_5',
                21: 'AEZ_6',
                27: 'AEZ_7',
                28: 'AEZ_8',
                32: 'AEZ_9'}
        df4 = df4.rename(columns=cols)
        print(df4.columns.tolist())
        print("df4 head:", df4.head())

        # making a copy of df4, because may run this cell a couple of times as I develop it
        df5 = df4.copy()

        # Get one hot encoding of columns 'soil_qual_high'
        one_hot1 = pd.get_dummies(df5['soil_qual_high'], dtype=int)
        # Drop original as it is now encoded
        df5 = df5.drop('soil_qual_high', axis=1)
        # Join the encoded df
        df5 = df5.join(one_hot1)

        print(len(df5))
        print(df5.head())
        print(df5.columns.tolist())
        # output was ['state_name', 'county_name', 'lon', 'lat', 'nutr_ret_high',
        #             'soil_qual_low', 'suit_irrig_high_soy', 'AEZ_1', 'AEZ_2', 'AEZ_3',
        #             'AEZ_4', 'AEZ_5', 'AEZ_6', 'AEZ_7', 'AEZ_8', 'AEZ_9',
        #             4, 5, 6, 7, 8, 9, 10]

        print()
        cols = {4: 'SQH_1',
                5: 'SQH_2',
                6: 'SQH_3',
                7: 'SQH_4',
                8: 'SQH_5',
                9: 'SQH_6',
                10: 'SQH_7'}
        df5 = df5.rename(columns=cols)
        print(df5.columns.tolist())
        print(df5.head())

        # making a copy of df5, because may run this cell a couple of times as I develop it
        df6 = df5.copy()

        # Get one hot encoding of columns 'soil_qual_low'
        one_hot2 = pd.get_dummies(df6['soil_qual_low'], dtype=int)
        # Drop original as it is now encoded
        df6 = df6.drop('soil_qual_low', axis=1)
        # Join the encoded df
        df6 = df6.join(one_hot2)

        print(len(df6))
        print(df6.head())
        print(df6.columns.tolist())
        # output was ['state_name', 'county_name', 'lon', 'lat', 'nutr_ret_high',
        #             'suit_irrig_high_soy', 'AEZ_1', 'AEZ_2', 'AEZ_3', 'AEZ_4',
        #             'AEZ_5', 'AEZ_6', 'AEZ_7', 'AEZ_8', 'AEZ_9',
        #             'SQH_1', 'SQH_2', 'SQH_3', 'SQH_4', 'SQH_5', 'SQH_6', 'SQH_7',
        #              4, 5, 6, 7, 8, 9, 10]

        print()
        cols = {4: 'SQL_1',
                5: 'SQL_2',
                6: 'SQL_3',
                7: 'SQL_4',
                8: 'SQL_5',
                9: 'SQL_6',
                10: 'SQL_7'}
        df6 = df6.rename(columns=cols)
        print(df6.columns.tolist())
        print(df6.head())

        self.archive_tiff(df6)
 
    def archive_tiff(self, tif_file):
        filename = 'state_county_lon_lat_soil.csv'
        tif_file.to_csv(archive_dir + filename, index=False)
        print('wrote file: ', archive_dir + filename)

url = {}

# using Land and Water Resources / Dominant AEZ class (33 classes) at 5 arc-minutes
# Based on 33 AEZ classes, even though pixel values are integer
url['AEZ_classes'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2red_5m_CRUTS32_Hist_8110_100_avg.tif"

# Using the URL of TIF file Soil Resources / Nutrient retention capacity, high inputs
# Based on 1 to 10, corresponding to bands 0.0 to 0.1; 0.1 to 02; etc.  So basically a numeric parameter
url['nutr_ret_high'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/soi1/SQ2_mze_v9aH.tif"

# using Land and Water Resources / Soil Resources / Most limiting soil quality rating factor, high inputs
# Based on 11 soil categories (and water), even though pixel values are integer
url['soil_qual_high'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/soi1/SQ0_mze_v9aH.tif"

# using Land and Water Resources / Soil Resources / Most limiting soil quality rating factor, low inputs
# same as previous
url['soil_qual_low'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/soi1/SQ0_mze_v9aL.tif"

# Leaving this one out because it is 43200 x 21600 pixels; don't want to work with different size input for now...
# using Land and Water Resources / Soil suitability, rain-fed, low-inputs
# url['soil_suit_rain_low'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/soi2/siLr_sss_mze.tif"

# using Suitability and Attainable Yield / Suitability Index / Suitability index range (0-10000);
# within this chose crop = wheat; time = 2011-2040; CO2 Fertilization = Yes; RCP 6.0; ClimateData(Random)
url['suit_irrig_high_soy'] = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp6p0/2020sH/sxHr_whe.tif"

tif_dir = "/Users/fuhsinliao/Downloads/ECS289L/Assignment3/GAEZ-SOIL-ML/"
archive_dir = '/Users/fuhsinliao/Downloads/ECS289L/Assignment3/'
scll_filename = 'state_county_lon_lat.csv'

if __name__ == "__main__":
    fs = FetchingSoil()
    fs.read_lonlat(archive_dir, scll_filename)
    fs.fetch_gaez_data(tif_dir, url)
    fs.fetch_meta_data()
    fs.pull_pixel_val()
    fs.combine_soil()