import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import  RFE
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
df=pd.read_csv('results.csv',index_col='Unnamed: 0')
df1=pd.read_csv('Transfer_value.csv')
df=pd.merge(df,df1)
df=df.replace('N/a',0)
df=df.drop(columns=['Unnamed: 0'])
def convert_age(age):
    try:
        if '-' in age:
            y, d = map(int, age.split('-'))
            return y + d / 365
        return int(age)
    except:
        return np.nan
    
df['Age'] = df['Age'].apply(convert_age)
df['Minutes']=df['Minutes'].str.replace(',','')
df['Minutes']=pd.to_numeric(df['Minutes'],errors='coerce')
df['Value'] = df['Value'].str.replace('€', '', regex=False)
df['Value'] = df['Value'].str.replace('M', '', regex=False)
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

df=pd.read_csv('new.csv')
# Create some new combined features from the basic features to help model identify important factors
def create_features(df):
    df['Performance'] = df['Goals'] + df['Assists']
    df['Experience'] = df['Age'] * df['Matches']
    df['Efficiency'] = df['Goals'] / df['Minutes'].replace(0, 1) * 90
    df['Defensive_Contribution'] = df['Tkl'] + df['Int'] + df['Blocks']
    df['Attack_Contribution'] = df['Goals'] + (df['Assists'] * 0.5)
    df['Minutes_per_Game'] = df['Minutes'] / df['Matches'].replace(0, 1)
    df['Age_Experience'] = df['Age'] * df['Experience']
    df['Performance_Efficiency'] = df['Performance'] * df['Efficiency']
    
    return df

def preprocess_data(df):
    z_scores = stats.zscore(df['Value'])
    df = df[(z_scores < 3) & (z_scores > -3)].copy()
    
    categorical_cols = ['Name', 'Nation', 'Team', 'Position']
    label_encoders = {}
    
    for col in categorical_cols:
        l = LabelEncoder()
        df[col] = l.fit_transform(df[col].astype(str))
        label_encoders[col] = l
    
    return df, label_encoders


def select_features(X, y):
    # Use RFE and XGBoost to choose the optimal features
    xgb = XGBRegressor(random_state=42)
    # In each iteration, RFE will remove 1 less important feature until the 20 most important features remain.
    rfe = RFE(estimator=xgb, n_features_to_select=20, step=1) 
    rfe.fit(X, y)
    
    # Get the selected features
    selected_columns = X.columns[rfe.support_]
    return selected_columns

def train_and_evaluate(X_train, y_train):
    # Automatically find optimal parameter combinations for XGBRegressor model via GridSearchCV.
    param_grid = {
        'n_estimators': [200, 300, 400], # the number of trees  in model 
        'max_depth': [4, 6, 8],# The maximum depth of each tree determines the complexity of the tree.
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 0.9, 1.0], # The proportion of data used to train each tree ( ex 80% 90% )
        'colsample_bytree': [0.8, 0.9, 1.0],# the proportion of feature used
        'min_child_weight': [1, 3, 5]
    }

    xgb = XGBRegressor(random_state=42)
    # Used GridSearchCV to find the best hyperparameters 
    grid_search = GridSearchCV(estimator=xgb,param_grid=param_grid,cv=5,scoring='neg_mean_squared_error',n_jobs=-1)
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

# Create new features and proprocess data
df = create_features(df) 
df, label_encoders = preprocess_data(df)

def main():
    features = df.drop('Value', axis=1)
    target = df['Value']
    
    # Standardize data
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    scaled_features = pd.DataFrame(scaled_features, columns=features.columns)
    
    # Choosing feature
    print(f"Selecting features...\n")
    selected_columns = select_features(scaled_features, target)
    selected_features = scaled_features[selected_columns]
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        selected_features, target, test_size=0.2, random_state=42
    )
    # Train model
    print(f"Training model...\n")
    model = train_and_evaluate(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print(f"Rmse: {rmse:.2f}")
    print(f"R2_score: {r2:.2f}")
    
    # Evaluate model more generally with cross validation
    cv_scores = cross_val_score(model, selected_features, target, cv=5, scoring='r2')
    print(f"Average R2 score: {cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': selected_columns,
        'Importance': model.feature_importances_* 100
    }).sort_values('Importance', ascending=False)
    
    print("\nImportance of features (%):")
    print(feature_importance)
    
    # Plot a bar chart of feature_importance
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=feature_importance)
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.show()
    plt.close()
    # Predict and show results
    Predictions = model.predict(selected_features)
    df['Predicted_Value'] = Predictions
    
    print("\nPredicted result for the first 10 plyers:")
    print(df[['Name', 'Value', 'Predicted_Value']].head(10))
    
if __name__ == "__main__":
    main()


