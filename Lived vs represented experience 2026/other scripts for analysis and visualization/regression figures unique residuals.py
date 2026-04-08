import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm


def generate_unique_contribution_figures_with_model_summary(csv_file, dependent_var, independent_vars, output_folder):
    """
    Generate regression plots showing the unique contribution of each independent variable
    based on a multiple regression model, including p-values, and export the model summary.
    
    Parameters:
        csv_file (str): Path to the CSV file.
        dependent_var (str): Dependent variable.
        independent_vars (list): List of independent variables.
        output_folder (str): Directory to save the regression plots and model summary.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Drop rows with missing data for the dependent and independent variables
    df = df[[dependent_var] + independent_vars].dropna()

    # Define X (independent variables) and y (dependent variable)
    X = df[independent_vars]
    y = df[dependent_var]

    # Add a constant for the intercept (required for statsmodels)
    X_with_const = sm.add_constant(X)

    # Fit the full model
    full_model = sm.OLS(y, X_with_const).fit()

    # Get the full model R-squared, coefficients, p-values, and standard errors
    full_r2 = full_model.rsquared
    coefficients = full_model.params
    p_values = full_model.pvalues
    std_errors = full_model.bse

    # Create a DataFrame with the full model summary
    model_summary_df = pd.DataFrame({
        "Coefficient": coefficients,
        "Standard Error": std_errors,
        "p-value": p_values,
    })
    model_summary_df.index.name = "Variable"
    model_summary_df["R-squared"] = full_r2

    # Save the model summary to a CSV file
    model_summary_csv = os.path.join(output_folder, "full_model_summary.csv")
    model_summary_df.to_csv(model_summary_csv)
    print(f"Full model summary saved to: {model_summary_csv}")

    # Print the full model summary to the console
    print("Full Model Summary:")
    print(full_model.summary())

    # Iterate through each independent variable to calculate and plot the unique contribution
    for ind_var in independent_vars:
        # Define the reduced model excluding the current variable
        reduced_X = X.drop(columns=[ind_var])
        reduced_X_with_const = sm.add_constant(reduced_X)

        # Fit the reduced model
        reduced_model = sm.OLS(y, reduced_X_with_const).fit()

        # Compute the reduced model R-squared
        reduced_r2 = reduced_model.rsquared

        # Compute the unique contribution of the current variable
        unique_contribution = full_r2 - reduced_r2
        p_value = p_values[ind_var]  # Get the p-value for the current variable
        coefficient = coefficients[ind_var]  # Get the coefficient for the current variable

        # Fit the partial regression for the current variable
        residual_y = y - reduced_model.predict(reduced_X_with_const)  # Residuals of y given the other variables
        residual_x = X[ind_var] - reduced_model.predict(reduced_X_with_const)  # Residuals of the current variable

        # Fit a regression line to the residuals
        partial_model = sm.OLS(residual_y, sm.add_constant(residual_x)).fit()
        x_pred = np.linspace(residual_x.min(), residual_x.max(), 100).reshape(-1, 1)
        y_pred = partial_model.predict(sm.add_constant(x_pred))

        # Plot the scatter and regression line
        plt.figure(figsize=(12, 8))
        plt.scatter(residual_x, residual_y, alpha=0.5, label='Residual Data Points')
        plt.plot(x_pred, y_pred, color='red', label=f'Residual Regression Line\n$R^2$ = {unique_contribution:.2f}')
        plt.xlabel(f'Residuals of {ind_var}', fontsize=16)
        plt.ylabel(f'Residuals of {dependent_var}', fontsize=16)
        plt.title(
            f'Unique Contribution of {ind_var} to {dependent_var}\n'
            f'p-value = {p_value:.4f}, Coefficient = {coefficient:.4f}',
            fontsize=18
        )
        plt.legend(fontsize=14)
        plt.grid(alpha=0.5, linestyle='--')
        plt.tight_layout()

        # Save the plot
        plot_filename = os.path.join(output_folder, f'{ind_var}_unique_contribution.png')
        plt.savefig(plot_filename, dpi=300)
        plt.close()

        print(f"Saved plot for {ind_var} vs {dependent_var} to {plot_filename}")


# Example usage
csv_file = 'csv file with relevant factor'
dependent_var = "Dependent variable"
independent_vars = ["factor1", "factor2", "factor3"]
# Independent variables
output_folder = "output folder/"  # Folder to save plots and summary

generate_unique_contribution_figures_with_model_summary(csv_file, dependent_var, independent_vars, output_folder)
