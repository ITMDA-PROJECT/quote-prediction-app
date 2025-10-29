import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import math
def dataprep(file_path):
    """Load and preprocess the data for model training."""
    data_raw = pd.read_excel(file_path)

    # Drop rows missing target or key features
    
    data = data_raw.replace('-',np.nan)
    data = data.dropna(subset='turnAroundDays')

    if len(data) == 0:
        raise ValueError("No valid rows found after cleaning. Check your Excel data.")

    # Convert orderDate to numeric days since first order
    data['orderDate'] = pd.to_datetime(data['orderDate'], errors='coerce')

    # Ensure numeric types for model
    data['actualTime (min)'] = pd.to_numeric(data['actualTime (min)'], errors='coerce')
    data['quantity'] = pd.to_numeric(data['quantity'], errors='coerce')
    data['turnAroundDays'] = pd.to_numeric(data['turnAroundDays'], errors='coerce')

    # Create Quarter feature
    data['Quarter']=data['orderDate'].dt.quarter

    # Convert categorical variables (materialCode, Quarter) into categorical
    if data['Quarter'].dtype != 'category':
        data['Quarter'] = data['Quarter'].astype('category')
    data[['materialType','materialc']]=data['materialCode'].str.split('-',expand=True)
    if data['materialType'].dtype != 'category':
        data['materialType'] = data['materialType'].astype('category')

    # Split into features and target
    feature_cols = ['actualTime (min)', 'materialType', 'quantity',  'Quarter' ]
    X = data[feature_cols]
    y = data['turnAroundDays']
    return X, y

def train_model(connection_string):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from xgboost import XGBRegressor

    X,y=dataprep(connection_string)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    #Training Model
    model = xgb.XGBRegressor(
                        objective = "reg:gamma",
                        eval_metric = 'gamma-nloglik',

                        max_leaves = 4,
                        n_estimators = 20,
                        learning_rate = 0.1,
                        min_child_weight = 5,

                        enable_categorical=True
                    )

    xgb_model = model.fit(X_train, y_train)
    
    return(xgb_model)
def model_performance(model,test_data_string,plot):
    
    R2_ls = [] #train, test
    mae_ls = []
    X,y=dataprep(test_data_string)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    # Make predictions
    y_pred = predict(model,X)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    y_train_pred_round = y_train_pred.round()
    y_test_pred_round = y_test_pred.round()

    mae_train = mean_absolute_error(y_train, y_train_pred_round)
    r2_train = r2_score(y_train, y_train_pred_round)

    mae_test = mean_absolute_error(y_test, y_test_pred_round)
    r2_test = r2_score(y_test, y_test_pred_round)

    R2_ls.append([round(r2_train,4), round(r2_test,4)])
    mae_ls.append([round(mae_train,2), round(mae_test,2)])

    results = pd.DataFrame(zip( R2_ls, mae_ls), columns=[ 'R2', 'MAE'])
    importance =pd.DataFrame(zip(model.feature_names_in_, model.feature_importances_))
    plt.figure(figsize=(12,5))

    # Actual vs Predicted
    plt.subplot(1,2,1)
    plt.scatter(x=y_train, y=y_train_pred_round, alpha=0.7)
    plt.xlabel("Actual Turnaround Time")
    plt.ylabel("Predicted Turnaround Time")
    plt.title(f"Actual vs Predicted (Train Set)\nR^2 ={r2_train:.2f}, MAE ={mae_train:.2f}")
    plt.grid(True)

    # Residual Distribution
    plt.subplot(1,2,2)
    residuals = y_train - y_train_pred_round
    plt.hist(residuals, bins=6, alpha=0.7)
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Distribution of Prediction Errors")

    plt.tight_layout()
    plt.show()
    plt.figure(figsize=(12,5))

    # Actual vs Predicted
    plt.subplot(1,2,1)
    plt.scatter(x=y_test, y=y_test_pred_round, alpha=0.7)
    plt.xlabel("Actual Turnaround Time")
    plt.ylabel("Predicted Turnaround Time")
    plt.title(f"Actual vs Predicted (Test Set)\nR^2 ={r2_test:.2f}, MAE ={mae_test:.2f}")
    plt.grid(True)

    # Residual Distribution
    plt.subplot(1,2,2)
    residuals = y_test - y_test_pred_round
    plt.hist(residuals, bins=4, alpha=0.7)
    plt.xlabel("Residuals")
    plt.ylabel("Frequency")
    plt.title("Distribution of Prediction Errors")

    plt.tight_layout()
    plt.show()

    return(results,importance)
def predict(model,x):
    
    final=model.predict(x)
    return(final.round())

#TESTING
if __name__ == "__main__":
    connection_string = "C:/Users/Thevesh/Desktop/Quotes_For_ML.xlsx"
    model = train_model(connection_string)
    #results, importance = model_performance(model,connection_string,plot=True)
    #print("Model Performance:\n", results)
    #print("Feature Importance:\n", importance)
    prediction_single = pd.DataFrame({
    'actualTime (min)': [30],
    'materialType': ['ALU6'],
    'quantity': [9],
    'Quarter': [4]
    })

    # Convert to proper dtypes
    prediction_single['materialType'] = prediction_single['materialType'].astype('category')
    prediction_single['Quarter'] = prediction_single['Quarter'].astype('category')

    # Make prediction
    print(predict(model, prediction_single))