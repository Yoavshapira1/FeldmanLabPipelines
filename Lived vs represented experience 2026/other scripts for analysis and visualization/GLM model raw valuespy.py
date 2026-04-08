 # -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:36:05 2025

@author: linoy.schwart
"""

#generic script used to calculate GLM 

import pandas as pd
import statsmodels.api as sm

# File path to the CSV (update with your actual file path)
csv_file_path = "OLS model csv with relevant facors"  # Replace with your CSV file path

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Automatically handle missing values by dropping rows with missing data in relevant columns
relevant_columns = ["factor1", "factor2", "factor3","factor 4"]
df = df[relevant_columns].dropna()

# Define the dependent and independent variables
X = df["factor1", "factor2", "factor3"]
#y = df["rest2 all"]
y = df["factor 4"]


# Add a constant for the intercept
X = sm.add_constant(X)

# Fit the GLM model
model = sm.OLS(y, X).fit()

# Print the model summary
print(model.summary())