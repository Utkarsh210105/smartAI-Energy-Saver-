import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
FORECAST_DIR = os.path.join(BASE_DIR, "forecast")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FORECAST_DIR, exist_ok=True)

def read_csv(path):
    return pd.read_csv(path)

def save_json(name, content):
    path = os.path.join(FORECAST_DIR, name)
    with open(path, "w") as f:
        json.dump(content, f, indent=4)

def clean_data(df):
    df = df.dropna()
    return df
