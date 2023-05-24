# -*- coding: utf-8 -*-
"""
Created on Fri May 19 11:12:09 2023

@author: user
"""
import urllib
import seaborn as sns


sns.set(style="darkgrid")

# Using the URL of TIF file Land and Water Resources / Land Cover / Cropland 
url = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res02/GFDL-ESM2M/rcp8p5/2080sH/grnd200b_yld.tif"

# Local directory to save the TIF file in
gaezDir = "D:\\Grad\\Food_Security\\Assignment2\\GAEZ\\"
tif_file_name = "peanuts_Rcp85_rainfed_2070_2100.tif"

# Fetch the TIF file using the URL
urllib.request.urlretrieve(url, gaezDir + tif_file_name)
