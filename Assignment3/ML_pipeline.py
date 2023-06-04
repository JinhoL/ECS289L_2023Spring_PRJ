# pulled this long list from somewhere and added to it.  Not using everything here

import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    f1_score,
)
from sklearn.model_selection import  train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Lasso
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import precision_recall_fscore_support, mean_squared_error, r2_score

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold

from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import numpy as np
import matplotlib.pyplot as plt
import math

archive_dir = '/Users/fuhsinliao/Downloads/ECS289L/Assignment3/'
ml_tables_dir = archive_dir
ml_file = 'Weather_Soil_Yield_Data.csv'

class MLPipeline():
    def __init__(self):
        self.df_ml = None

    def read_weekly_file(self):

        self.df_ml = pd.read_csv(ml_tables_dir + ml_file)
        print(self.df_ml.shape)
        print(self.df_ml.head())

        # Happily, there are no null values in my ML table
        print(self.df_ml.isnull().values.any())
        # yields False

        X = self.df_ml.drop(columns=['yield'])
        y = self.df_ml.loc[:,['yield']]

        print(X.shape)
        print(y.shape)
        # print(X.head())
        # print(y.head())
        return X, y

    def create_training_set(self, x, y):
        # For this pipeline I will do random shuffling of the input records before separating the test set
        # Choosing random_state=0 (or any specific integer) will ensure that different runs will use same shuffle

        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

        # keeping a copy of y_test, because it may get modified below
        y_test_orig = y_test.copy()

        print(X_train.head())
        print(y_train.head())
        print(X_test.head())
        print("ytest.head",y_test.head())
        print()
        print(y_test_orig.head())
        # note: index of first row in y_test_orig is 7397)

        print()
        print(X_train.shape)
        print(X_test.shape)
        print(y_train.shape)
        print(y_test.shape)
        print()
        print(y_test.iloc[0,0])

        X_train = X_train.drop(columns=['year', 'state_name', 'county_name'])
        X_test = X_test.drop(columns=['year', 'state_name', 'county_name'])

        scalerXST = StandardScaler().fit(X_train)
        scaleryST = StandardScaler().fit(y_train)

        X_trainST = scalerXST.transform(X_train)
        y_trainST = scaleryST.transform(y_train)
        X_testST = scalerXST.transform(X_test)
        y_testST = scaleryST.transform(y_test)

        # testing how inverse of the scaling is working

        # basically, if scalery was your scaling function, then use scalery.inverse_transform;
        #   NOTE: this works on a sequence

        #print(type(len(X_trainST)), y_testST[0], list(y_test)[0])
        print(self.df_ml.iloc[len(X_trainST)]['yield'])  # the first entry in y_test has index 1277 from df_ml
        #print(y_testST[0])  # .loc[[1277]])
        print(scaleryST.inverse_transform(y_testST)[0])

        # confusingly, you set the "lambda" variable of LASSO algorithm using the parameter "alpha"
        # alpha can take values between 0 and 1; using 1.0 is "full penalty", so maximum attempts to remove features
        # lassoST = Lasso(alpha=1.0)
        # lassoST = Lasso(alpha=0.5)
        # lassoST = Lasso(alpha=0.2)
        lassoST = Lasso(alpha=0.1)
        lassoST.fit(X_trainST, y_trainST)
        y_predST = lassoST.predict(X_testST)
        print(y_predST)
        rmseST = math.sqrt(mean_squared_error(y_testST, y_predST))
        print(rmseST)
        # Example usage
        # y_test = np.array([1, 2, 3, 4, 5])
        # y_pred = np.array([1.1, 1.9, 3.2, 3.8, 4.9])
        self.plot_predictions(y_testST, y_predST, 'Lasso with StandardScalar')

    # Try linear regression
        linearST = LinearRegression()
        print(type(y_trainST))
        linearST.fit(X_trainST, y_trainST)
        y_predST = linearST.predict(X_testST)
        rmseST = math.sqrt(mean_squared_error(y_testST, y_predST))
        print(rmseST)
        self.plot_predictions(y_testST, y_predST, 'Linear Regression using StandardScaler')

    # Min max scalar ver. of linear regression
        scalerXMM = MinMaxScaler().fit(X_train)
        scaleryMM = MinMaxScaler().fit(y_train)

        X_trainMM = scalerXMM.transform(X_train)
        y_trainMM = scaleryMM.transform(y_train)
        X_testMM = scalerXMM.transform(X_test)
        y_testMM = scaleryMM.transform(y_test)

        # testing how inverse of the scaling is working with MinMaxScaler
        print("yield:",self.df_ml.iloc[len(X_trainST)]['yield'])  # the first entry in y_test has index 1277 from df_ml
        print(y_testMM[0])
        print(scaleryMM.inverse_transform(y_testMM)[0])
        linearMM = LinearRegression()
        linearMM.fit(X_trainMM, y_trainMM)
        y_predMM = linearMM.predict(X_testMM)
        rmseMM = math.sqrt(mean_squared_error(y_testMM, y_predMM))
        rrmseMM = rmseMM / (0.5)
        r2MM = r2_score(y_testMM, y_predMM)
        print(rmseMM)
        print(rrmseMM)
        print(r2MM)
        self.plot_predictions(y_testMM, y_predMM, 'Linear Regression using MinMaxScaler')

    # random forest regressor
        # regrMM = RandomForestRegressor(max_depth=2, random_state=0)
        #   with depth 2
        #      0.11073969374036899
        #      0.22147938748073798
        #      0.3119899078797479
        # regrMM = RandomForestRegressor(max_depth=10, random_state=0)
        #   with depth 10:
        #      0.062301254023809476
        #      0.12460250804761895
        #      0.7822381741106176
        regrMM = RandomForestRegressor(max_depth=20, random_state=0)
        #   with depth 20:
        #      0.06060039414793919
        #      0.12120078829587838
        #      0.7939659164434344

        # for some reason, need to use y_trainMM.ravel() rather than simply y_trainMM
        regrMM.fit(X_trainMM, y_trainMM.ravel())
        y_predMM = regrMM.predict(X_testMM)
        rmseMM = math.sqrt(mean_squared_error(y_testMM, y_predMM))
        rrmseMM = rmseMM / (0.5)
        r2MM = r2_score(y_testMM, y_predMM)
        print(rmseMM)
        print(rrmseMM)
        print(r2MM)
        self.plot_predictions(y_testMM, y_predMM, 'Random Forest Regressor using MinMaxScaler')

    # from chatGPT!
    def plot_predictions(self,y_test, y_pred, descrip_of_run):
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
        plt.show()

if __name__ == "__main__":
    m = MLPipeline()
    x, y = m.read_weekly_file()
    m.create_training_set(x, y)
