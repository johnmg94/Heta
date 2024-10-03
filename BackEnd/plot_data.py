# plot_data.py

import matplotlib.pyplot as plt
import pandas as pd

def plot_series(df, x_col, y_col, title):
    plt.figure(figsize=(12, 6))
    print("Type X Col:" + str(type(x_col)))
    plt.plot(df[x_col], df[y_col])
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == '__main__':
    from run_sql import run_query
    gdp_df = run_query('SELECT * FROM gdp')
    plot_series(gdp_df, 'Date', 'GDP', 'GDP Over Time')
