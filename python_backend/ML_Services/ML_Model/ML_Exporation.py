import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import metrics
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import LabelEncoder
#Importing data
data = pd.read_excel('your excel file path here') #Replace with your excel file path
new_data=data
data['orderDate'] = data['orderDate'].replace('-', pd.NA)

# Drop rows where date is missing
data = data.dropna(subset=['orderDate'])

# Convert to datetime
data['orderDate'] = pd.to_datetime(data['orderDate'])
data = data.sort_values('orderDate')

#Splitting date into 4 quaters
data['Quarter']=data['orderDate'].dt.quarter
data=pd.get_dummies(data, columns=['Quarter'], prefix='Q')
print (data)

#Setting features and goal terms
X=data[['materialCode','actualTime (min)','quantity','Q_1','Q_2','Q_3','Q_4']]
X=pd.get_dummies(X,columns=['materialCode'],drop_first=True)
X = X.astype({col: 'int' for col in X.select_dtypes('bool').columns})
y=data['turnAroundDays']
y = y.astype(str).str.strip()

# Convert to numeric
y = pd.to_numeric(y, errors='coerce')
y = y.loc[y.notna()]

#making sure that all are same lenth
X,y=X.align(y,join='inner',axis=0)

#splitting features into training 
X_train,X_val,y_train,y_val=train_test_split(X,y,test_size=0.2,random_state=45)

#Double-check feature data types
print("Feature types:\n", X_train.dtypes)
#print(X.head())
print("\nTarget type:", y_train.dtype)

# Add constant for intercept
X_train = sm.add_constant(X_train, has_constant='add')

#Fitting models on training
model = sm.OLS(y_train, X_train).fit()
model2= sm.GLM(y_train,X_train,family=sm.families.Gaussian()).fit()
model3=sm.WLS(y_train,X_train,weights=1/X_train['quantity']).fit()
model4=sm.GLSAR(y_train,X_train,rho=1).fit()

#Summaries of models
print(model.summary())
#print(model2.summary())
#print(model3.summary())
#print(model4.summary())

#Comparing stats
comparison={
    'Model':['OLS','WLS','GLM','GLSAR'],
    'AIC':[model.aic, model2.aic ,model3.aic,model4.aic],
    'BIC':[model.bic, model2.bic ,model3.bic,model4.bic],
    'Adj.R2':[model.rsquared_adj,None ,model3.rsquared_adj,model4.rsquared_adj],
    'RMSE':[((model.resid**2).mean())**0.5,((model2.resid_response**2).mean())**0.5,((model3.resid**2).mean())**0.5,((model4.resid**2).mean())**0.5,]
}
print(pd.DataFrame(comparison))

#Showing residuales for OLS
#plt.scatter(y_train,model.resid)
#plt.axhline(0,color='red')
#plt.title("OLS residuales")
#plt.show()

#Testing trainnig agaist validation
X_val=sm.add_constant(X_val)

#Baseline RMSE based on mean
y_mean=y_train.mean()
baseline_rmse=np.sqrt(((y_val-y_mean)**2).mean())
print("Baseline RMSE: ",baseline_rmse)

#Testing RMSE on OLS
y_pred=model.predict(X_val)
rmse=np.sqrt(((y_val-y_pred)**2).mean())
print ("Validation RMSE on OLS: ",rmse)
nrmse = rmse / (y_val.max() - y_val.min())
print("NRMSE:", nrmse)

plt.scatter(y_train,(model.predict(X_train)).round())
plt.xlabel("Actual Time (days)")
plt.ylabel("Predicted Time (days)")
plt.title("Model Predictions vs Actual Times")
plt.show()
'''
#Testing RMSE on WLS
y_pred=model2.predict(X_val)
rmse=np.sqrt(((y_val-y_pred)**2).mean())
#print ("Validation RMSE on WLS: ",rmse)
nrmse = rmse / (y_val.max() - y_val.min())
#print("NRMSE:", nrmse)

#Testing RMSE on GLM
y_pred=model3.predict(X_val)
rmse=np.sqrt(((y_val-y_pred)**2).mean())
#print ("Validation RMSE on GLM: ",rmse)
nrmse = rmse / (y_val.max() - y_val.min())
#print("NRMSE:", nrmse)

#Testing RMSE on GLSAR
y_pred=model4.predict(X_val)
rmse=np.sqrt(((y_val-y_pred)**2).mean())
#print ("Validation RMSE on GLSAR: ",rmse)
nrmse = rmse / (y_val.max() - y_val.min())
#print("NRMSE:", nrmse)
'''
#xgboost every boost is anouther tree, build a tree, get ans, have error, use error to build anouther tree, repeat
#tuning, max depth or number of leaves(leaves are better?)
X=new_data[['materialCode','actualTime (min)','quantity','orderDate']]
if 'materialCode' in X.columns:
    le=LabelEncoder()
    X['materialCode']=le.fit_transform(X['materialCode'].astype(str))
if 'orderDate' in X.columns:
    X['orderDate'] = pd.to_datetime(X['orderDate'], errors='coerce')
    X['month'] = X['orderDate'].dt.month
    X.drop('orderDate', axis=1, inplace=True)
X,y=X.align(y,join='inner',axis=0)
X_train,X_val,y_train,y_val=train_test_split(X,y,test_size=0.2,random_state=45)
leaves_ls = []
estimators_ls = []
min_child_ls = []
train_ls = [] #[R2, RMSE, MGD, MPD]
val_ls = []
oot_ls = []

R2_ls = [] #train, val, test
mae_ls = []
mgd_ls = []
mpd_ls = []
for num_leaves in np.arange(3, 4,1):
    for num_boost in np.arange(15, 16, 5):
        for min_child in np.arange(5, 6, 1):

            leaves_ls.append(num_leaves)
            estimators_ls.append(num_boost)
            min_child_ls.append(min_child)
            
            model = xgb.XGBRegressor(
                objective = "reg:gamma",
                eval_metric = 'gamma-nloglik',

                max_leaves = num_leaves,    
                n_estimators = num_boost, 
                learning_rate = 0.1,
                min_child_weight = min_child,

                enable_categorical=True
            )

            xgb_model = model.fit(X_train, y_train)

            y_train_preds = xgb_model.predict(X_train)
            y_val_preds = xgb_model.predict(X_val)
            
            
            r2_train = metrics.r2_score(y_train, y_train_preds)
            mae_train = metrics.mean_absolute_error(y_train, y_train_preds)
            mgd_train = metrics.mean_gamma_deviance(y_train, y_train_preds)
            mpd_train = metrics.mean_poisson_deviance(y_train, y_train_preds)

            # train_ls.append([round(r2_train, 4), round(rmse_train, 4), round(mgd_train, 4), round(mpd_train, 4)])

            r2_val = metrics.r2_score(y_val, y_val_preds)
            mae_val = metrics.mean_absolute_error(y_val, y_val_preds)
            mgd_val = metrics.mean_gamma_deviance(y_val, y_val_preds)
            mpd_val = metrics.mean_poisson_deviance(y_val, y_val_preds)

            # val_ls.append([r2_val, rmse_val, mgd_val, mpd_val])

            

            
            R2_ls.append([round(r2_train,4), round(r2_val,4)])
            mae_ls.append([round(mae_train,2), round(mae_val,2)])
            mgd_ls.append([round(mgd_train,4), round(mgd_val,4)])
            mpd_ls.append([round(mpd_train,4), round(mpd_val,4)])

            
results = pd.DataFrame(zip(leaves_ls, estimators_ls, min_child_ls, R2_ls, mae_ls, mgd_ls, mpd_ls), columns=['leaves', 'estimators', 'min_child_weight', 'R2', 'MAE', 'MGD', 'MPD'])
print(results)
importance =pd.DataFrame(zip(xgb_model.feature_names_in_, xgb_model.feature_importances_))
print(importance)