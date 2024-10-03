# regression_analysis.py

import statsmodels.api as sm
import pandas as pd

def run_regression(df, dependent_var, independent_vars):
    X = df[independent_vars]
    y = df[dependent_var]
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    return model

# Example usage
if __name__ == '__main__':
    from run_sql import run_query
    gdp_df = run_query('SELECT * FROM gdp')
    gdp_df['Time'] = pd.to_datetime(gdp_df['Date']).astype(int) / 10**9  # Convert dates to timestamps
    model = run_regression(gdp_df, 'GDP', ['Time'])
    print(model.summary())
