import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_tips(csv_path):
    df = pd.read_csv(csv_path)

    if "Units_Consumed_kWh" not in df.columns:
        raise ValueError("CSV must contain column 'Units_Consumed_kWh'.")

    df = df.reset_index(drop=True).copy()
    df["y"] = df["Units_Consumed_kWh"]
    df["month_index"] = np.arange(1, len(df) + 1)
    df["usage_change"] = df["y"].diff().fillna(0)
    avg_usage = df["y"].mean()

    # Usage category
    def classify(v):
        if v < avg_usage * 0.9: return 0
        if v < avg_usage * 1.1: return 1
        return 2

    df["category"] = df["y"].apply(classify)

    X = df[["month_index", "y", "usage_change"]].values
    y_label = df["category"].values

    tree = DecisionTreeClassifier(max_depth=3, random_state=42)
    tree.fit(X, y_label)

    predicted_class = int(tree.predict(X[-1].reshape(1, -1))[0])

    classes = ["Low", "Medium", "High"]

    tips_map = {
        0: ["Great job! Keep conserving energy.", 
            "Turn off devices fully instead of standby.",
            "Use natural daylight whenever possible.",
            "Unplug chargers when not in use.",
            "Maintain fan efficiency by cleaning blades."],

        1: ["Your usage is moderate.",
            "Switch to LED bulbs.",
            "Run appliances like washing machines only with full loads.",
            "Maintain AC at 24–26°C.",
            "Avoid peak-hour usage."],

        2: ["High usage detected!",
            "Clean your AC filters regularly.",
            "Avoid unnecessary geyser/heater usage.",
            "Check for faulty or old appliances.",
            "Shift heavy appliances to off-peak hours."]
    }

    # Save decision tree
    forecast_dir = os.path.join(os.path.dirname(__file__), "forecast")
    os.makedirs(forecast_dir, exist_ok=True)
    path = os.path.join(forecast_dir, "tips_tree.png")

    plt.figure(figsize=(8, 5))
    plot_tree(tree, feature_names=["month_index", "usage", "usage_change"],
              class_names=classes, filled=True, rounded=True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return {
        "predicted_class": predicted_class,
        "category": classes[predicted_class],
        "tips": tips_map[predicted_class]
    }
