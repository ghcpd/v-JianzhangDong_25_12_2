import pandas as pd

def load_csv(path: str):
    """
    Load CSV with pandas and return DataFrame.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    return df
