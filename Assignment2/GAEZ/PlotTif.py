# -*- coding: utf-8 -*-
"""
Created on Wed May 17 21:12:46 2023

@author: user
"""



import tifffile
import matplotlib.pyplot as plt

# Open the TIF file
image = tifffile.imread("D:\\Grad\\Food_Security\\Assignment2\\GAEZ\\peanuts_Rcp85_rainfed_2070_2100.tif")

# Define the cropping coordinates (left, upper, right, lower)
crop_coordinates = (3360, 770, 3490, 900)
cropped_image = image[crop_coordinates[1]:crop_coordinates[3], crop_coordinates[0]:crop_coordinates[2]]

# Display the plot
plt.imshow(cropped_image)
plt.colorbar()

plt.savefig("D:\\Grad\\Food_Security\\Assignment2\\GAEZ\\peanuts_gaez_Rcp85_rainfed_2070_2100.png", dpi=3600)













