# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 16:13:12 2025

@author: linoy.schwart
"""
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from tqdm import tqdm

def bootstrap_mediation(data, X, M, Y, n_boots=20000, seed=42):
    """
    Conduct mediation analysis using bootstrapping.
    """
    # Handle missing values
    data_clean = data[[X, M, Y]].dropna()
    n = len(data_clean)
    
    print(f"Original sample size: {len(data)}")
    print(f"Complete cases: {n}")
    
    np.random.seed(seed)
    
    # Original models
    # Total effect (c path)
    model_c = sm.OLS(data_clean[Y], sm.add_constant(data_clean[X])).fit()
    print("\n=== Total Effect Model (Y ~ X) ===")
    print(model_c.summary())
    
    # a path
    model_a = sm.OLS(data_clean[M], sm.add_constant(data_clean[X])).fit()
    print("\n=== Path a Model (M ~ X) ===")
    print(model_a.summary())
    
    # Full model (b path and c' path)
    X_M = pd.DataFrame({X: data_clean[X], M: data_clean[M]})
    model_b = sm.OLS(data_clean[Y], sm.add_constant(X_M)).fit()
    print("\n=== Full Model (Y ~ X + M) ===")
    print(model_b.summary())
    
    # Original effects
    c = model_c.params[X]
    a = model_a.params[X]
    b = model_b.params[M]
    c_prime = model_b.params[X]
    indirect = a * b
    
    # Bootstrap procedure
    print("\nRunning bootstrap procedure...")
    boot_effects = {
        'a': np.zeros(n_boots),
        'b': np.zeros(n_boots),
        'c': np.zeros(n_boots),
        'c_prime': np.zeros(n_boots),
        'indirect': np.zeros(n_boots),
        'prop_mediated': np.zeros(n_boots)
    }
    
    for i in tqdm(range(n_boots)):
        # Sample with replacement
        boot_idx = np.random.choice(n, size=n, replace=True)
        boot_data = data_clean.iloc[boot_idx]
        
        # Compute effects for this bootstrap sample
        boot_c = sm.OLS(boot_data[Y], sm.add_constant(boot_data[X])).fit().params[X]
        boot_a = sm.OLS(boot_data[M], sm.add_constant(boot_data[X])).fit().params[X]
        boot_b_model = sm.OLS(boot_data[Y], sm.add_constant(pd.DataFrame({
            X: boot_data[X],
            M: boot_data[M]
        }))).fit()
        boot_b = boot_b_model.params[M]
        boot_c_prime = boot_b_model.params[X]
        boot_indirect = boot_a * boot_b
        
        # Store results
        boot_effects['a'][i] = boot_a
        boot_effects['b'][i] = boot_b
        boot_effects['c'][i] = boot_c
        boot_effects['c_prime'][i] = boot_c_prime
        boot_effects['indirect'][i] = boot_indirect
        boot_effects['prop_mediated'][i] = boot_indirect / boot_c if boot_c != 0 else np.nan
    
    # Calculate confidence intervals and p-values
    def calc_ci_and_p(values, original):
        ci = np.percentile(values[~np.isnan(values)], [2.5, 97.5])
        p = 2 * min(
            np.mean(values[~np.isnan(values)] <= 0) if original > 0 else np.mean(values[~np.isnan(values)] >= 0),
            0.5
        )
        return ci, p
    
    # Calculate results for each effect
    results = {}
    for effect in boot_effects:
        if effect == 'prop_mediated':
            ci, p = calc_ci_and_p(boot_effects[effect], indirect/c)
            est = indirect/c
        else:
            ci, p = calc_ci_and_p(boot_effects[effect], locals()[effect])
            est = locals()[effect]
        
        results[effect] = {
            'estimate': est,
            'ci': ci,
            'p': p,
            'se': np.nanstd(boot_effects[effect])
        }
    
    # Print results
    print("\n=== Mediation Analysis Results ===")
    print(f"\nDirect Effect (c'):")
    print(f"Estimate: {results['c_prime']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['c_prime']['se']:.4f}")
    print(f"95% CI: [{results['c_prime']['ci'][0]:.4f}, {results['c_prime']['ci'][1]:.4f}]")
    print(f"p-value: {results['c_prime']['p']:.4f}")
    
    print(f"\nIndirect Effect (a*b):")
    print(f"Estimate: {results['indirect']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['indirect']['se']:.4f}")
    print(f"95% CI: [{results['indirect']['ci'][0]:.4f}, {results['indirect']['ci'][1]:.4f}]")
    print(f"p-value: {results['indirect']['p']:.4f}")
    
    print(f"\nTotal Effect (c):")
    print(f"Estimate: {results['c']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['c']['se']:.4f}")
    print(f"95% CI: [{results['c']['ci'][0]:.4f}, {results['c']['ci'][1]:.4f}]")
    print(f"p-value: {results['c']['p']:.4f}")
    
    print(f"\nPath a (X → M):")
    print(f"Estimate: {results['a']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['a']['se']:.4f}")
    print(f"95% CI: [{results['a']['ci'][0]:.4f}, {results['a']['ci'][1]:.4f}]")
    print(f"p-value: {results['a']['p']:.4f}")
    
    print(f"\nPath b (M → Y):")
    print(f"Estimate: {results['b']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['b']['se']:.4f}")
    print(f"95% CI: [{results['b']['ci'][0]:.4f}, {results['b']['ci'][1]:.4f}]")
    print(f"p-value: {results['b']['p']:.4f}")
    
    print(f"\nProportion Mediated:")
    print(f"Estimate: {results['prop_mediated']['estimate']:.4f}")
    print(f"Bootstrap SE: {results['prop_mediated']['se']:.4f}")
    print(f"95% CI: [{results['prop_mediated']['ci'][0]:.4f}, {results['prop_mediated']['ci'][1]:.4f}]")
    
    return results, boot_effects

if __name__ == "__main__":
    try:
        # Read data
        file_path = "csv file with relevant factors for mediation analysis"
        data = pd.read_csv(file_path)
        
        # Run analysis
        results, boot_effects = bootstrap_mediation(
            data=data,
            X="Live Social Experience Neural Synchrony",
            M="Behavioral Synchrony",
            Y="Represented Social Exerience Neural Synchrony",
            #n_simulations=10000,
            n_boots=20000
        )
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your data and variable names.")
        print("Please check your data and variable names.")