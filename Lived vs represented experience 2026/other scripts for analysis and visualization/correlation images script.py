import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from matplotlib.patches import Rectangle


# generic script for correlation plots and distribution with 95 CI and statistcal parameters 
#names of columns should change based on the factors relevant for the correlation

# Set style
sns.set_style("white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# Read data
data = pd.read_csv('csv file for correlation')
data.columns = ['Live_Neural_Synchrony', 'Represented_Neural_Synchrony']

# Remove any NaN values
data = data.dropna()

print(f"Data loaded: n = {len(data)} observations")
print(f"Live Neural Synchrony: M = {data['Live_Neural_Synchrony'].mean():.4f}, SD = {data['Live_Neural_Synchrony'].std():.4f}")
print(f"Represented Neural Synchrony: M = {data['Represented_Neural_Synchrony'].mean():.4f}, SD = {data['Represented_Neural_Synchrony'].std():.4f}")

# Calculate correlation and statistics
r, p = stats.pearsonr(data['Live_Neural_Synchrony'], data['Represented_Neural_Synchrony'])
n = len(data)

# Calculate 95% CI using Fisher's Z transformation
z = np.arctanh(r)
se = 1/np.sqrt(n-3)
z_crit = stats.norm.ppf(0.975)
ci_lower = np.tanh(z - z_crit * se)
ci_upper = np.tanh(z + z_crit * se)

print(f"\nCorrelation statistics:")
print(f"r = {r:.3f}")
print(f"p = {p:.4f}")
print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")

# Calculate regression line
slope, intercept = np.polyfit(data['Live_Neural_Synchrony'], data['Represented_Neural_Synchrony'], 1)

# Calculate symmetric axis limit
max_val = max(data['Live_Neural_Synchrony'].max(), data['Represented_Neural_Synchrony'].max()) * 1.05

x_line = np.array([0, max_val])
y_line = slope * x_line + intercept

# Calculate confidence and prediction intervals
def prediction_interval(x, y, x_pred, confidence=0.95):
    """Calculate prediction interval for regression"""
    n = len(x)
    y_pred = slope * x_pred + intercept
    
    # Residual standard error
    residuals = y - (slope * x + intercept)
    rse = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    # Standard error of prediction
    x_mean = np.mean(x)
    sxx = np.sum((x - x_mean)**2)
    se_pred = rse * np.sqrt(1 + 1/n + (x_pred - x_mean)**2 / sxx)
    
    # t-value for confidence level
    t_val = stats.t.ppf((1 + confidence) / 2, n - 2)
    
    margin = t_val * se_pred
    return y_pred - margin, y_pred + margin

def confidence_interval(x, y, x_pred, confidence=0.95):
    """Calculate confidence interval for regression line"""
    n = len(x)
    y_pred = slope * x_pred + intercept
    
    # Residual standard error
    residuals = y - (slope * x + intercept)
    rse = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    # Standard error of mean prediction
    x_mean = np.mean(x)
    sxx = np.sum((x - x_mean)**2)
    se_conf = rse * np.sqrt(1/n + (x_pred - x_mean)**2 / sxx)
    
    # t-value for confidence level
    t_val = stats.t.ppf((1 + confidence) / 2, n - 2)
    
    margin = t_val * se_conf
    return y_pred - margin, y_pred + margin

# Generate prediction and confidence bands
x_pred = np.linspace(0, max_val, 200)
ci_lower_band, ci_upper_band = confidence_interval(
    data['Live_Neural_Synchrony'].values, 
    data['Represented_Neural_Synchrony'].values, 
    x_pred
)
pi_lower_band, pi_upper_band = prediction_interval(
    data['Live_Neural_Synchrony'].values, 
    data['Represented_Neural_Synchrony'].values, 
    x_pred
)

# Create figure with marginal distributions
fig = plt.figure(figsize=(10, 10))

# Define grid
gs = fig.add_gridspec(4, 4, hspace=0.05, wspace=0.05)

# Main scatter plot
ax_main = fig.add_subplot(gs[1:4, 0:3])

# Scatter plot
scatter = ax_main.scatter(
    data['Live_Neural_Synchrony'], 
    data['Represented_Neural_Synchrony'],
    alpha=0.6,
    s=80,
    c='#4A90E2',
    edgecolors='white',
    linewidths=1,
    zorder=3
)

# Regression line
ax_main.plot(
    x_line, 
    y_line, 
    color='#E74C3C', 
    linewidth=2.5, 
    label=f'Regression line (r = {r:.2f})',
    zorder=2
)

# Confidence interval
ax_main.fill_between(
    x_pred,
    ci_lower_band,
    ci_upper_band,
    alpha=0.2,
    color='#E74C3C',
    label='95% Confidence Interval',
    zorder=1
)

# Prediction interval
ax_main.fill_between(
    x_pred,
    pi_lower_band,
    pi_upper_band,
    alpha=0.1,
    color='#95A5A6',
    label='95% Prediction Interval',
    zorder=0
)

# Set axis limits to be symmetric
max_val = max(data['Live_Neural_Synchrony'].max(), data['Represented_Neural_Synchrony'].max()) * 1.05
ax_main.set_xlim(0, max_val)
ax_main.set_ylim(0, max_val)

# Labels
ax_main.set_xlabel('Live Social Experience Neural Synchrony (wPLI)', fontsize=13, fontweight='bold')
ax_main.set_ylabel('Represented Social Experience Neural Synchrony (wPLI)', fontsize=13, fontweight='bold')

# Grid
ax_main.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
ax_main.set_axisbelow(True)

# Legend
ax_main.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)

# Add statistics box in upper right to avoid data
stats_text = (
    f'n = {n}\n'
    f'r = {r:.3f}\n'
    f'p = {p:.4f}\n'
    f'95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]'
)
ax_main.text(
    0.98, 0.98, 
    stats_text,
    transform=ax_main.transAxes,
    fontsize=11,
    verticalalignment='top',
    horizontalalignment='right',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'),
    fontfamily='monospace'
)

# Top histogram (Live Neural Synchrony distribution)
ax_top = fig.add_subplot(gs[0, 0:3], sharex=ax_main)
ax_top.hist(
    data['Live_Neural_Synchrony'], 
    bins=20, 
    color='#4A90E2', 
    alpha=0.7,
    edgecolor='white',
    linewidth=1
)
ax_top.set_xlim(0, max_val)
ax_top.axis('off')

# Add KDE overlay
from scipy.stats import gaussian_kde
kde_x = gaussian_kde(data['Live_Neural_Synchrony'])
x_range = np.linspace(0, max_val, 200)
ax_top_twin = ax_top.twinx()
ax_top_twin.plot(x_range, kde_x(x_range), color='#2C3E50', linewidth=2)
ax_top_twin.fill_between(x_range, kde_x(x_range), alpha=0.2, color='#4A90E2')
ax_top_twin.axis('off')

# Right histogram (Represented Neural Synchrony distribution)
ax_right = fig.add_subplot(gs[1:4, 3], sharey=ax_main)
ax_right.hist(
    data['Represented_Neural_Synchrony'], 
    bins=20, 
    orientation='horizontal',
    color='#4A90E2', 
    alpha=0.7,
    edgecolor='white',
    linewidth=1
)
ax_right.set_ylim(0, max_val)
ax_right.axis('off')

# Add KDE overlay
kde_y = gaussian_kde(data['Represented_Neural_Synchrony'])
y_range = np.linspace(0, max_val, 200)
ax_right_twin = ax_right.twiny()
ax_right_twin.plot(kde_y(y_range), y_range, color='#2C3E50', linewidth=2)
ax_right_twin.fill_betweenx(y_range, kde_y(y_range), alpha=0.2, color='#4A90E2')
ax_right_twin.axis('off')

# Title
fig.suptitle(
    'Live Social Experience Neural Synchrony Predicts Represented Social Experience Neural Synchrony',
    fontsize=14,
    fontweight='bold',
    y=0.98
)

# Tight layout
plt.tight_layout()

# Save figure
plt.savefig('/mnt/user-data/outputs/live_represented_correlation_distributions.png', dpi=300, bbox_inches='tight')
plt.savefig('/mnt/user-data/outputs/live_represented_correlation_distributions.pdf', dpi=300, bbox_inches='tight')

print("\nFigure saved to:")
print("  - live_represented_correlation_distributions.png")
print("  - live_represented_correlation_distributions.pdf")

# Create a simpler version without marginal distributions
fig2, ax = plt.subplots(figsize=(8, 6))

# Scatter plot
ax.scatter(
    data['Live_Neural_Synchrony'], 
    data['Represented_Neural_Synchrony'],
    alpha=0.6,
    s=80,
    c='#4A90E2',
    edgecolors='white',
    linewidths=1,
    zorder=3
)

# Regression line
ax.plot(x_line, y_line, color='#E74C3C', linewidth=2.5, zorder=2)

# Confidence interval
ax.fill_between(x_pred, ci_lower_band, ci_upper_band, alpha=0.2, color='#E74C3C', zorder=1)

# Prediction interval
ax.fill_between(x_pred, pi_lower_band, pi_upper_band, alpha=0.1, color='#95A5A6', zorder=0)

# Set symmetric limits
max_val = max(data['Live_Neural_Synchrony'].max(), data['Represented_Neural_Synchrony'].max()) * 1.05
ax.set_xlim(0, max_val)
ax.set_ylim(0, max_val)

# Labels
ax.set_xlabel('Live Social Experience Neural Synchrony (wPLI)', fontsize=13, fontweight='bold')
ax.set_ylabel('Represented Social Experience Neural Synchrony (wPLI)', fontsize=13, fontweight='bold')

# Title
ax.set_title(
    f'r = {r:.3f}, p = {p:.4f}, 95% CI [{ci_lower:.3f}, {ci_upper:.3f}]',
    fontsize=12,
    pad=15
)

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
ax.set_axisbelow(True)

# Statistics box - positioned to avoid data
stats_text = f'n = {n}\nr = {r:.3f}\np = {p:.4f}\n95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]'
ax.text(
    0.98, 0.30,
    stats_text,
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment='top',
    horizontalalignment='right',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'),
    fontfamily='monospace'
)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/live_represented_correlation_simple.png', dpi=300, bbox_inches='tight')
plt.savefig('/mnt/user-data/outputs/live_represented_correlation_simple.pdf', dpi=300, bbox_inches='tight')

print("  - live_represented_correlation_simple.png")
print("  - live_represented_correlation_simple.pdf")

print("\nDone!")
