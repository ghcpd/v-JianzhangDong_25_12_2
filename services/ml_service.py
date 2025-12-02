from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def train_simple_model(df: pd.DataFrame):
    """
    Train a simple linear regression using the first numeric column as target.
    """
    numeric_df = df.select_dtypes(include=['int64', 'float64'])

    if numeric_df.shape[1] < 2:
        raise ValueError("Need at least 2 numeric columns to train model.")

    X = numeric_df.iloc[:, 1:].values
    y = numeric_df.iloc[:, 0].values

    model = LinearRegression()
    model.fit(X, y)
    return model
