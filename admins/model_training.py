import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error 
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.path.join(BASE_DIR, 'models')
DEFAULT_MODEL_FILENAME = 'sales_prediction_model.pkl'
DEFAULT_MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILENAME)


def upload_dataset(uploaded_file):
    """Save an uploaded CSV file and return the local file path."""
    if uploaded_file is None:
        raise ValueError('No file provided for upload.')

    upload_dir = os.path.join(BASE_DIR, 'media', 'datasets')
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.name)

    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path


def load_dataset(dataset_path):
    """Load a CSV dataset from disk into a pandas DataFrame."""
    if not dataset_path or not os.path.exists(dataset_path):
        raise FileNotFoundError(f'Dataset not found at {dataset_path}')

    return pd.read_csv(dataset_path)


def preprocess_data(df):
    """Preprocess data and return features and target arrays."""
    if 'Weekly_Sales' not in df.columns:
        raise ValueError("Expected target column 'Weekly_Sales' in dataset.")

    df_clean = df.copy()

    # Convert Date column if present, then derive time features.
    if 'Date' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'],dayfirst=True,errors='coerce')
        df_clean['Year'] = df_clean['Date'].dt.year
        df_clean['Month'] = df_clean['Date'].dt.month
        df_clean['Week'] = df_clean['Date'].dt.isocalendar().week
        df_clean['Quarter'] = df_clean['Date'].dt.quarter
        df_clean = df_clean.drop(columns=['Date'])

    # Drop rows that do not have target values.
    df_clean = df_clean.dropna(subset=['Weekly_Sales'])

    # Fill numeric missing values with median.
    numeric_columns = df_clean.select_dtypes(include=['number']).columns.tolist()
    numeric_columns = [col for col in numeric_columns if col != 'Weekly_Sales']
    for column in numeric_columns:
        if df_clean[column].isna().any():
            df_clean[column] = df_clean[column].fillna(df_clean[column].median())

    # Encode categorical columns.
    categorical_columns = df_clean.select_dtypes(include=['object']).columns.tolist()
    for column in categorical_columns:
        df_clean[column] = df_clean[column].astype('category').cat.codes

    X = df_clean.drop(columns=['Weekly_Sales'])
    y = df_clean['Weekly_Sales']
    return X, y


def split_dataset(X, y, test_size=0.2, random_state=42):
    """Split features and target into training and testing sets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def fit_model(X_train, y_train):
    """Train all models and return them."""

    models = {
        "Decision Tree": DecisionTreeRegressor(
            random_state=42
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=42
        ),

        "XGBoost": XGBRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    }

    for model in models.values():
        model.fit(X_train, y_train)

    return models
def train_model(models, X_train, X_test, y_train, y_test):
    """Evaluate all models."""

    results = {}

    best_model = None
    best_algorithm = None
    best_score = -1

    for name, model in models.items():

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_score = r2_score(y_train, y_train_pred)
        test_score = r2_score(y_test, y_test_pred)

        results[name] = {
            "train_score": round(train_score, 4),
            "test_score": round(test_score, 4),
            "mae": round(mean_absolute_error(y_test, y_test_pred), 2),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_test_pred)), 2),
        }

        if test_score > best_score:
            best_score = test_score
            best_model = model
            best_algorithm = name

    return results, best_model, best_algorithm
def save_model(model, model_path=None):
    """Save the trained model to disk and return the saved path."""
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    return model_path
