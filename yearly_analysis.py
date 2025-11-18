import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_year_comparison(df):
    plt.figure(figsize=(9, 5))
    years = df["Billing_Year"].unique()

    for year in years:
        year_data = df[df["Billing_Year"] == year]
        plt.plot(year_data["Billing_Month"], year_data["Units_Consumed_kWh"],
                 marker="o", label=str(year))

    plt.title("Year-over-Year Electricity Usage Comparison")
    plt.xlabel("Month")
    plt.ylabel("Usage (kWh)")
    plt.legend(title="Year")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    path = os.path.join("forecast", "year_comparison.png")
    plt.savefig(path)
    plt.close()
    return path


def plot_year_averages(df):
    avg = df.groupby("Billing_Year")["Units_Consumed_kWh"].mean()

    plt.figure(figsize=(7, 4))
    plt.bar(avg.index.astype(str), avg.values, color="skyblue")
    plt.title("Average Electricity Usage Per Year")
    plt.ylabel("Average kWh")
    plt.xlabel("Year")
    plt.tight_layout()

    path = os.path.join("forecast", "year_avg.png")
    plt.savefig(path)
    plt.close()
    return path



