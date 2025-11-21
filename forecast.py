import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from utils import read_csv, save_json, clean_data, FORECAST_DIR


def run_forecast(filepath: str, rate_per_unit: float = 6.0) -> dict:
    # Read & Clean
    df = read_csv(filepath)
    df = clean_data(df)

    y_col = "Units_Consumed_kWh"
    if y_col not in df.columns:
        raise ValueError(f"{y_col} not found in CSV")

    df = df.reset_index(drop=True)

    #  Cyclical Encoding for Month Seasonality
    df["sin_month"] = np.sin(2 * np.pi * df["Billing_Month"] / 12)
    df["cos_month"] = np.cos(2 * np.pi * df["Billing_Month"] / 12)

    # ---- Features (X) and Target (y) ----
    X = df[["sin_month", "cos_month"]].values
    y = df[y_col].values

    #  Train/Test Split 
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=142
    )

    #  Random Forest Model 
    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluation Metrics 
    y_pred_test = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred_test))
    r2 = float(r2_score(y_test, y_pred_test))

    # Forecast next month
    next_month = (df["Billing_Month"].iloc[-1] % 12) + 1

    next_features = np.array([
        [
            np.sin(2 * np.pi * next_month / 12),
            np.cos(2 * np.pi * next_month / 12)
        ]
    ])

    predicted_usage = float(model.predict(next_features)[0])
    predicted_bill = float(predicted_usage * rate_per_unit)

    #  Predict for full graph
    y_pred_full = model.predict(X)

    # Save JSON 
    save_json("forecast.json", {
        "previous_months": df.to_dict(orient="records"),
        "predicted_usage_kWh": round(predicted_usage, 2),
        "predicted_bill_inr": round(predicted_bill, 2),
        "rate_per_unit": rate_per_unit,
        "mae_units": round(mae, 2),
        "r2_score": round(r2, 4),
    })

    #  Plot 
    plt.figure(figsize=(8, 4))
    sns.lineplot(x=df["Billing_Month"], y=y, marker="o", label="Actual")
    sns.lineplot(x=df["Billing_Month"], y=y_pred_full, label="RF Seasonal Fit")
    plt.scatter(next_month, predicted_usage, color="red", s=100, label="Next Forecast")

    plt.title("Electricity Usage Forecast (Random Forest Seasonal)", fontsize=12)
    plt.xlabel("Billing Month")
    plt.ylabel("Usage (kWh)")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(FORECAST_DIR, "forecast_plot.png")
    plt.savefig(plot_path)
    plt.close()

    return {
        "predicted_usage_kWh": round(predicted_usage, 2),
        "predicted_bill_inr": round(predicted_bill, 2),
        "mae_units": round(mae, 2),
        "r2_score": round(r2, 4)
    }
