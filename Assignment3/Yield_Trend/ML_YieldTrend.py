# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 15:19:40 2023

@author: user
"""

import math
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import  train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression, Lasso
from sklearn.metrics import precision_recall_fscore_support, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor



def plot_predictions(y_test, y_pred, descrip_of_run):
    # Check if the arrays have the same length
    if len(y_test) != len(y_pred):
        raise ValueError("The input arrays must have the same length.")

    # Create a scatter plot
    plt.scatter(y_test, y_pred)
    plt.plot(y_test, y_test, color='red', linestyle='--')  # Line y_pred = y_test
    plt.xlabel('y_test')
    plt.ylabel('y_pred')
    plt.title('Predicted vs Actual for ' + descrip_of_run)
    plt.grid(True)
    
    plt.savefig(descrip_of_run + '.png')
    plt.show()
    




kansasYield = pd.read_csv('D:\\Grad\\Food_Security\\Assignment3\\Yield_Trend_Data.csv')
print(kansasYield)


kansasYield = kansasYield.drop('yield', axis=1)
#kansasYield = kansasYield.drop('year', axis=1)
kansasYield = kansasYield.drop('county_name', axis=1)
kansasYield = kansasYield.drop('state_name', axis=1)
kansasYield = kansasYield.drop('lon', axis=1)
kansasYield = kansasYield.drop('lat', axis=1)

X = kansasYield.drop(columns=['accumulated_yield'])
Y = kansasYield.loc[:,['accumulated_yield']]
print(X)
print(Y)


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
y_test_orig = y_test.copy()


scalerXST = StandardScaler().fit(X_train)
scaleryST = StandardScaler().fit(y_train)

X_trainST = scalerXST.transform(X_train)
y_trainST = scaleryST.transform(y_train)
X_testST = scalerXST.transform(X_test)
y_testST = scaleryST.transform(y_test)


# Lasso
lassoST = Lasso(alpha=0.1)
lassoST.fit(X_trainST, y_trainST)
y_predST = lassoST.predict(X_testST)
print(y_predST)
rmseST = math.sqrt(mean_squared_error(y_testST, y_predST))
print(rmseST)
# Example usage
# y_test = np.array([1, 2, 3, 4, 5])
# y_pred = np.array([1.1, 1.9, 3.2, 3.8, 4.9])
plot_predictions(y_testST, y_predST, 'Lasso with StandardScalar (Accumulated Yield)')


# Linear Regression
linearST = LinearRegression()
print(type(y_trainST))

linearST.fit(X_trainST, y_trainST)
y_predST = linearST.predict(X_testST)
rmseST = math.sqrt(mean_squared_error(y_testST, y_predST))
print(rmseST)


plot_predictions(y_testST, y_predST, 'Linear Regression using StandardScaler (Accumulated Yield)')



# Min max scalar ver. of linear regression
scalerXMM = MinMaxScaler().fit(X_train)
scaleryMM = MinMaxScaler().fit(y_train)

X_trainMM = scalerXMM.transform(X_train)
y_trainMM = scaleryMM.transform(y_train)
X_testMM = scalerXMM.transform(X_test)
y_testMM = scaleryMM.transform(y_test)


linearMM = LinearRegression()
linearMM.fit(X_trainMM, y_trainMM)
y_predMM = linearMM.predict(X_testMM)
rmseMM = math.sqrt(mean_squared_error(y_testMM, y_predMM))
rrmseMM = rmseMM / (0.5)
r2MM = r2_score(y_testMM, y_predMM)
print(rmseMM)
print(rrmseMM)
print(r2MM)
plot_predictions(y_testMM, y_predMM, 'Linear Regression using MinMaxScaler (Accumulated Yield)')


# random forest regressor
regrMM = RandomForestRegressor(max_depth=20, random_state=0)

regrMM.fit(X_trainMM, y_trainMM.ravel())
y_predMM = regrMM.predict(X_testMM)
rmseMM = math.sqrt(mean_squared_error(y_testMM, y_predMM))
rrmseMM = rmseMM / (0.5)
r2MM = r2_score(y_testMM, y_predMM)
print(rmseMM)
print(rrmseMM)
print(r2MM)
plot_predictions(y_testMM, y_predMM, 'Random Forest Regressor using MinMaxScaler (Accumulated Yield)')

# =============================================================================
# 
# # Predict the yield trend
# sumnerYield = yieldDf[yieldDf['county_name'] == 'SUMNER']
# #sumnerAccumulatedYield = sumnerYield.loc[:,['yield']]
# sumnerYield = sumnerYield.drop('accumulated_yield', axis=1)
# sumnerYield = sumnerYield.drop('year', axis=1)
# sumnerYield = sumnerYield.drop('county_name', axis=1)
# sumnerYield = sumnerYield.drop('state_name', axis=1)
# sumnerYield = sumnerYield.drop('lon', axis=1)
# sumnerYield = sumnerYield.drop('lat', axis=1)
# 
# 
# X_predST = scalerXST.transform(sumnerYield)
# y_predST = linearST.predict(X_predST)
# y_pred = y_predST
# y_pred = scaleryST.inverse_transform(y_predST)
# 
# 
# # =============================================================================
# # for i in range(len(y_pred)-2, -1, -1):
# #     y_pred[i + 1] = y_pred[i + 1] - y_pred[i]
# # 
# # print(y_pred)
# # =============================================================================
# 
# # Plot Sumner Yield Trend
# years = [year for year in range(3, 23)]
# 
# plt.plot(years, y_pred, label='Predict')
# #plt.plot(years, sumnerAccumulatedYield, color='red', label='Actual')
# 
# plt.xlabel('year')
# plt.ylabel(' yield')
# plt.title('Predict vs Actual of Sumner Yield Trend')
# plt.xticks(range(min(years), max(years)+1))
# plt.legend()
# 
# plt.show()
# =============================================================================













