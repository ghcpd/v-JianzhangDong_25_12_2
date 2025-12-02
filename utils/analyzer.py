import numpy as np
import pandas as pd

def summarize_data(df: pd.DataFrame):
    """
    Return basic summary statistics.
    """
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "mean_values": df.mean(numeric_only=True).to_dict(),
        "std_values": df.std(numeric_only=True).to_dict(),
        "null_count": df.isnull().sum().to_dict()
    }
    return summary
