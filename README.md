# ECS289L_2023Spring_PRJ
ECS 289L, 2023 Spring Quarter, Project Github.

## Assignment 1
- The report and the contribution of each team memeber are in the "report file"
- The FAO data and Tableau graphs are in the "export folder" and the "import folder".
- Data preprocessing and Sankey graph are in the "sankey folder"



## Assignment 2

- Weather

  - NASA POWER (2011 - 2022)

  - Community Climate System Model (CCSM) (2023 - 2100)

    > Download data from here: https://gis.ucar.edu/gis-climatedata

- GAEZ

  - Get a .tif file link from: https://gaez.fao.org/pages/data-viewer



## Assignment 3

1. Fetch yield, lon_lat, soil, and weather csv files.
2. Run "Merge_Weather_Soil_Yield_Weekly.ipynb" to generate weekly data for ML.
3. ML pipeline (2 approaches)
   - Original method: Run "ML_pipeline.py"
   - Yield Trend method: run "generateKansasAccumulatedYieldData.py" and "ML_YieldTrend.py"
