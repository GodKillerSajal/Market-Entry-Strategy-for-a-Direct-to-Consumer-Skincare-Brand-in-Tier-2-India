"""
Project 1: Market-Entry Strategy for a D2C Skincare Brand in Tier-2 India
Script 04: Visualizations — 10 High-Quality Charts
===============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import json
import os

# Font setup for potential CJK characters
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Style
plt.style.use('seaborn-v0_8-whitegrid')
PALETTE = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4', '#E94F37', '#393E41']
sns.set_palette(PALETTE)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Load all processed data
df = pd.read_csv(os.path.join(RAW_DIR, "consumer_survey_data.csv"))
seg_df = pd.read_csv(os.path.join(PROCESSED_DIR, "segmented_survey_data.csv"))
comp_df = pd.read_csv(os.path.join(PROCESSED_DIR, "competitive_positioning.csv"))
demand_gaps = pd.read_csv(os.path.join(PROCESSED_DIR, "demand_gap_detail.csv"), index_col=0)
corr_matrix = pd.read_csv(os.path.join(PROCESSED_DIR, "correlation_matrix.csv"), index_col=0)
city_stats = pd.read_csv(os.path.join(PROCESSED_DIR, "city_wise_stats.csv"), index_col=0)
concerns = pd.read_csv(os.path.join(PROCESSED_DIR, "skin_concerns.csv"), index_col=0)
categories = pd.read_csv(os.path.join(PROCESSED_DIR, "category_interest.csv"), index_col=0)
monthly = pd.read_csv(os.path.join(PROCESSED_DIR, "monthly_breakdown_24m.csv"))

with open(os.path.join(PROCESSED_DIR, "gtm_recommendations.json")) as f:
    gtm = json.load(f)


def save_fig(fig, name, dpi=150):
    fig.savefig(os.path.join(OUTPUTS_DIR, name), dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  Saved: {name}")


# =============================================================================
# CHART 1: Market Sizing Funnel (Top-Down TAM → SAM → SOM)
# =============================================================================
print("Generating charts...")

fig, ax = plt.subplots(figsize=(10, 6))
steps = pd.read_csv(os.path.join(PROCESSED_DIR, "market_sizing_steps.csv"))
# Show top-down funnel (skip TAM row for clarity)
funnel = steps.iloc[3:7].copy()  # Online, Tier-2, SAM, SOM
labels = [
    "Online Channel\n(Rs 49,500 Cr)",
    "Tier-2 Cities\n(Rs 17,325 Cr = SAM)",
    "SAM (Top-Down)\n(Rs 17,325 Cr)",
    "Year 1 SOM\n(Rs 866 Cr)"
]
values = funnel["Value_INR_Crore"].values

colors = ['#2E86AB', '#44BBA4', '#F18F01', '#C73E1D']
bars = ax.barh(range(len(labels)), values, color=colors, height=0.6, edgecolor='white', linewidth=1.5)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=11, fontweight='bold')
ax.invert_yaxis()
ax.set_xlabel('Market Size (Rs Crore)', fontsize=12, fontweight='bold')
ax.set_title('Top-Down Market Sizing: India D2C Skincare → Tier-2 SAM',
             fontsize=14, fontweight='bold', pad=15)

# Add value labels
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + max(values)*0.02, bar.get_y() + bar.get_height()/2,
            f'Rs {val:,.0f} Cr', va='center', fontsize=10, fontweight='bold', color='#333')

ax.set_xlim(0, max(values) * 1.25)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '01_market_sizing_funnel.png')


# =============================================================================
# CHART 2: Consumer Survey — Demographics Overview (City + Age Group)
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# City distribution
city_order = df['city'].value_counts().index
city_counts = df['city'].value_counts()
axes[0].barh(city_order, city_counts.values, color=PALETTE[:8], height=0.6, edgecolor='white')
axes[0].set_xlabel('Number of Respondents', fontsize=11)
axes[0].set_title('Survey Coverage by City', fontsize=13, fontweight='bold')
for i, v in enumerate(city_counts.values):
    axes[0].text(v + 10, i, str(v), va='center', fontsize=9, fontweight='bold')

# Age group distribution
age_counts = df['age_group'].value_counts().sort_index()
wedges, texts, autotexts = axes[1].pie(age_counts.values, labels=age_counts.index,
                                        autopct='%1.1f%%', colors=PALETTE[:3],
                                        startangle=90, textprops={'fontsize': 11})
for t in autotexts:
    t.set_fontweight('bold')
axes[1].set_title('Age Group Distribution', fontsize=13, fontweight='bold')

fig.suptitle('Consumer Survey Demographics (N=5,500)', fontsize=15, fontweight='bold', y=1.02)
fig.tight_layout()
save_fig(fig, '02_demographics_overview.png')


# =============================================================================
# CHART 3: Spending Distribution by Income Bracket
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
income_order = ['<15K', '15K-25K', '25K-50K', '50K-75K', '>75K']
spend_data = [df[df['income_bracket'] == ib]['current_skincare_spend_monthly'] for ib in income_order]

bp = ax.boxplot(spend_data, labels=income_order, patch_artist=True, widths=0.5,
                medianprops={'color': '#C73E1D', 'linewidth': 2},
                whiskerprops={'linewidth': 1.2}, capprops={'linewidth': 1.2})
for patch, color in zip(bp['boxes'], PALETTE[:5]):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)

# Add mean markers
means = [s.mean() for s in spend_data]
ax.scatter(range(1, 6), means, color='#C73E1D', marker='D', s=80, zorder=5, label='Mean')
ax.set_xlabel('Monthly Income Bracket (Rs)', fontsize=12, fontweight='bold')
ax.set_ylabel('Monthly Skincare Spend (Rs)', fontsize=12, fontweight='bold')
ax.set_title('Monthly Skincare Spend by Income Bracket', fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '03_spending_by_income.png')


# =============================================================================
# CHART 4: Price Sensitivity & Natural Preference by City
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

city_price = df.groupby('city')['price_sensitivity'].mean().sort_values(ascending=True)
city_natural = df.groupby('city')['natural_preference'].mean().sort_values(ascending=True)

axes[0].barh(city_price.index, city_price.values, color='#2E86AB', height=0.6, edgecolor='white')
axes[0].set_xlabel('Average Price Sensitivity (1-10)', fontsize=11)
axes[0].set_title('Price Sensitivity by City\n(Higher = More Sensitive)', fontsize=12, fontweight='bold')
axes[0].axvline(x=city_price.mean(), color='#C73E1D', linestyle='--', linewidth=1.5, label=f'Avg: {city_price.mean():.1f}')
axes[0].legend(fontsize=10)
for i, v in enumerate(city_price.values):
    axes[0].text(v + 0.05, i, f'{v:.1f}', va='center', fontsize=9)

axes[1].barh(city_natural.index, city_natural.values, color='#44BBA4', height=0.6, edgecolor='white')
axes[1].set_xlabel('Average Natural Preference (1-10)', fontsize=11)
axes[1].set_title('Natural/Clean Beauty Preference by City\n(Higher = Prefers Natural)', fontsize=12, fontweight='bold')
axes[1].axvline(x=city_natural.mean(), color='#C73E1D', linestyle='--', linewidth=1.5, label=f'Avg: {city_natural.mean():.1f}')
axes[1].legend(fontsize=10)
for i, v in enumerate(city_natural.values):
    axes[1].text(v + 0.05, i, f'{v:.1f}', va='center', fontsize=9)

fig.suptitle('Consumer Behavior Metrics Across Tier-2 Cities', fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
save_fig(fig, '04_price_natural_by_city.png')


# =============================================================================
# CHART 5: Correlation Heatmap
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 8))
numeric_cols = ['age', 'current_skincare_spend_monthly', 'brand_loyalty_score',
                'price_sensitivity', 'natural_preference', 'purchase_frequency',
                'willingness_to_try_new_brand', 'social_media_influence',
                'satisfaction_current_products']
short_labels = ['Age', 'Monthly Spend', 'Brand Loyalty', 'Price Sensitivity',
                'Natural Pref.', 'Purchase Freq.', 'Willingness to Try',
                'Social Media Inf.', 'Satisfaction']

sns.heatmap(corr_matrix.values, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            xticklabels=short_labels, yticklabels=short_labels, ax=ax,
            square=True, linewidths=0.5, cbar_kws={'shrink': 0.8},
            vmin=-1, vmax=1, annot_kws={'size': 9})
ax.set_title('Correlation Matrix: Key Consumer Metrics', fontsize=14, fontweight='bold', pad=15)
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(fontsize=9)
fig.tight_layout()
save_fig(fig, '05_correlation_heatmap.png')


# =============================================================================
# CHART 6: Channel Preference by Age Group (Stacked Bar)
# =============================================================================
fig, ax = plt.subplots(figsize=(9, 6))
channel_by_age = pd.read_csv(os.path.join(PROCESSED_DIR, "channel_by_age.csv"), index_col=0)
channel_colors = {'Online': '#2E86AB', 'Offline': '#F18F01', 'Both': '#44BBA4'}

channel_by_age.plot(kind='bar', stacked=True, ax=ax, color=[channel_colors.get(c, '#999') for c in channel_by_age.columns],
                    width=0.5, edgecolor='white', linewidth=1.5)
ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax.set_title('Channel Preference by Age Group', fontsize=14, fontweight='bold', pad=15)
ax.legend(title='Channel', fontsize=10, title_fontsize=11, bbox_to_anchor=(1.02, 1))
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11)
ax.set_ylim(0, 100)
for c in ax.containers:
    ax.bar_label(c, fmt='%.1f%%', label_type='center', fontsize=9, fontweight='bold', color='white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '06_channel_preference_by_age.png')


# =============================================================================
# CHART 7: Demand Gap Analysis — Opportunity Score
# =============================================================================
fig, ax = plt.subplots(figsize=(12, 6))
dg = demand_gaps.sort_values('Opportunity_Score', ascending=True)
colors = ['#44BBA4' if v >= 5.8 else '#F18F01' if v >= 5.5 else '#E94F37' for v in dg['Opportunity_Score']]
bars = ax.barh(dg.index, dg['Opportunity_Score'], color=colors, height=0.6, edgecolor='white', linewidth=1)
ax.set_xlabel('Opportunity Score', fontsize=12, fontweight='bold')
ax.set_title('Demand Gap Analysis: Product Category Opportunities\n(Higher = Bigger White Space)',
             fontsize=13, fontweight='bold', pad=15)

for bar, val in zip(bars, dg['Opportunity_Score']):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=10, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#44BBA4', label='High Opportunity (>=5.8)'),
                   Patch(facecolor='#F18F01', label='Medium Opportunity (5.5-5.8)'),
                   Patch(facecolor='#E94F37', label='Lower Opportunity (<5.5)')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '07_demand_gap_analysis.png')


# =============================================================================
# CHART 8: Competitive Positioning Map (Price vs. Natural)
# =============================================================================
fig, ax = plt.subplots(figsize=(11, 7))

# Remove duplicate mCaffeine (has both mCaffeine and MCaffeine)
comp_plot = comp_df.drop_duplicates(subset='Brand', keep='first').copy()
# Also remove the duplicate
comp_plot = comp_plot[~comp_plot['Brand'].isin(['mCaffeine'])]  # Keep MCaffeine only

quadrant_colors = {
    'High Price + High Natural': '#44BBA4',
    'Low Price + High Natural': '#2E86AB',
    'High Price + Low Natural': '#F18F01',
    'Low Price + Low Natural': '#E94F37',
}

for quad, color in quadrant_colors.items():
    mask = comp_plot['Quadrant'] == quad
    if mask.any():
        ax.scatter(comp_plot.loc[mask, 'Price_Score'], comp_plot.loc[mask, 'Natural_Score'],
                   s=comp_plot.loc[mask, 'Market_Presence'] * 500 + 100,
                   c=color, alpha=0.8, edgecolors='white', linewidth=2, label=quad, zorder=5)

# Label each brand
for _, row in comp_plot.iterrows():
    ax.annotate(row['Brand'], (row['Price_Score'], row['Natural_Score']),
                textcoords='offset points', xytext=(10, 5), fontsize=9, fontweight='bold',
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.8))

# Add quadrant lines
median_p = comp_plot['Price_Score'].median()
median_n = comp_plot['Natural_Score'].median()
ax.axhline(y=median_n, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(x=median_p, color='gray', linestyle='--', linewidth=1, alpha=0.7)

# Quadrant labels
ax.text(0.95, 0.95, 'Premium Natural', transform=ax.transAxes, ha='right', va='top',
        fontsize=10, fontstyle='italic', color='gray', alpha=0.8)
ax.text(0.05, 0.95, 'Mass Natural', transform=ax.transAxes, ha='left', va='top',
        fontsize=10, fontstyle='italic', color='gray', alpha=0.8)
ax.text(0.95, 0.05, 'Premium Chemical', transform=ax.transAxes, ha='right', va='bottom',
        fontsize=10, fontstyle='italic', color='gray', alpha=0.8)
ax.text(0.05, 0.05, 'Mass Chemical', transform=ax.transAxes, ha='left', va='bottom',
        fontsize=10, fontstyle='italic', color='gray', alpha=0.8)

ax.set_xlabel('Price Positioning →', fontsize=12, fontweight='bold')
ax.set_ylabel('Natural/Clean Beauty Score →', fontsize=12, fontweight='bold')
ax.set_title('Competitive Positioning Map: D2C Skincare Brands\n(Bubble size = Market Presence)',
             fontsize=13, fontweight='bold', pad=15)
ax.legend(fontsize=9, loc='center left', bbox_to_anchor=(1.02, 0.5))
ax.set_xlim(2, 9)
ax.set_ylim(2, 10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '08_competitive_positioning_map.png')


# =============================================================================
# CHART 9: Customer Segmentation Profile (Radar-style grouped bar)
# =============================================================================
fig, ax = plt.subplots(figsize=(12, 6))

seg_profiles = pd.read_csv(os.path.join(PROCESSED_DIR, "segment_profiles.csv"), index_col=0)
metrics_to_plot = ['avg_natural_pref', 'avg_price_sens', 'avg_willingness', 'avg_social_media', 'd2c_awareness_pct']
metric_labels = ['Natural\nPreference', 'Price\nSensitivity', 'Willingness\nto Try', 'Social Media\nInfluence', 'D2C\nAwareness %']

# Normalize to 0-10 scale
plot_data = seg_profiles[metrics_to_plot].copy()
plot_data['d2c_awareness_pct'] = plot_data['d2c_awareness_pct'] / 10  # Convert % to /10

x = np.arange(len(metric_labels))
width = 0.18
seg_colors = ['#2E86AB', '#F18F01', '#A23B72', '#44BBA4']

for i, (seg_name, row) in enumerate(plot_data.iterrows()):
    # Get the human-readable name
    seg_label = seg_profiles.loc[seg_name, 'name']
    values = row[metrics_to_plot].values
    values[4] = values[4] / 10 * 10  # Already normalized
    bars = ax.bar(x + i * width, values, width, label=seg_label, color=seg_colors[i],
                  edgecolor='white', linewidth=1)

ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
ax.set_ylabel('Score (0-10)', fontsize=12, fontweight='bold')
ax.set_title('Customer Segment Profiles: Key Behavioral Metrics',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(metric_labels, fontsize=10)
ax.legend(title='Segment', fontsize=9, title_fontsize=10, bbox_to_anchor=(1.02, 1))
ax.set_ylim(0, 10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
save_fig(fig, '09_segment_profiles.png')


# =============================================================================
# CHART 10: 3-Year Financial Projection + Break-Even
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Monthly revenue & cumulative EBITDA
ax1 = axes[0]
ax1b = ax1.twinx()

months = monthly['Month'].values
revenue = monthly['Revenue_Lakhs'].values
cum_ebitda = monthly['Cumulative_EBITDA_Lakhs'].values

ax1.bar(months, revenue, color='#2E86AB', alpha=0.7, label='Monthly Revenue', width=0.7)
ax1b.plot(months, cum_ebitda, color='#C73E1D', linewidth=2.5, marker='o', markersize=4,
          label='Cumulative EBITDA')

# Break-even line
be_month = None
for i, v in enumerate(cum_ebitda):
    if v >= 0:
        be_month = months[i]
        break
if be_month:
    ax1b.axhline(y=0, color='gray', linestyle=':', linewidth=1)
    ax1b.axvline(x=be_month, color='#44BBA4', linestyle='--', linewidth=2, label=f'Break-even (Month {be_month})')
    ax1.annotate(f'Break-even\nMonth {be_month}', xy=(be_month, 0),
                 xytext=(be_month + 2, max(cum_ebitda)*0.3),
                 arrowprops=dict(arrowstyle='->', color='#44BBA4', lw=1.5),
                 fontsize=10, fontweight='bold', color='#44BBA4')

ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
ax1.set_ylabel('Monthly Revenue (Rs Lakhs)', fontsize=11, color='#2E86AB')
ax1b.set_ylabel('Cumulative EBITDA (Rs Lakhs)', fontsize=11, color='#C73E1D')
ax1.set_title('Revenue Ramp & Break-Even Analysis', fontsize=13, fontweight='bold', pad=15)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
ax1.spines['top'].set_visible(False)

# Right: 3-Year P&L Summary
ax2 = axes[1]
fin_data = pd.DataFrame({
    'Year': ['Year 1', 'Year 2', 'Year 3'],
    'Revenue': [2.0, 8.5, 22.0],
    'COGS': [1.2, 4.68, 11.0],
    'Marketing': [0.6, 2.12, 4.4],
    'EBITDA': [-0.16, 0.51, 3.96],
})

x2 = np.arange(3)
w2 = 0.18
ax2.bar(x2 - 1.5*w2, fin_data['Revenue'], w2, label='Revenue', color='#2E86AB', edgecolor='white')
ax2.bar(x2 - 0.5*w2, fin_data['COGS'], w2, label='COGS', color='#E94F37', edgecolor='white')
ax2.bar(x2 + 0.5*w2, fin_data['Marketing'], w2, label='Marketing', color='#F18F01', edgecolor='white')
ebitda_colors = ['#C73E1D' if v < 0 else '#44BBA4' for v in fin_data['EBITDA']]
ax2.bar(x2 + 1.5*w2, fin_data['EBITDA'], w2, label='EBITDA', color=ebitda_colors, edgecolor='white')

ax2.set_xticks(x2)
ax2.set_xticklabels(fin_data['Year'], fontsize=11)
ax2.set_ylabel('Amount (Rs Crore)', fontsize=11, fontweight='bold')
ax2.set_title('3-Year P&L Summary', fontsize=13, fontweight='bold', pad=15)
ax2.legend(fontsize=9)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add EBITDA values on bars
for i, v in enumerate(fin_data['EBITDA']):
    label = f'{v:.1f} Cr' if v >= 0 else f'({abs(v):.1f} Cr)'
    ax2.text(i + 1.5*w2, v + 0.3 if v >= 0 else v - 0.5, label, ha='center', fontsize=9,
             fontweight='bold', color=ebitda_colors[i])

fig.suptitle('Financial Projections', fontsize=16, fontweight='bold', y=1.02)
fig.tight_layout()
save_fig(fig, '10_financial_projections.png')


# =============================================================================
# BONUS CHART: Marketing Mix & Channel Strategy
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Marketing Mix Donut
ax1 = axes[0]
mkt_labels = ['Influencer Marketing\n(Instagram/YouTube)', 'Google Search Ads',
              'Sample Boxes', 'Offline Activations']
mkt_pcts = [40, 25, 20, 15]
mkt_colors = ['#A23B72', '#2E86AB', '#44BBA4', '#F18F01']

wedges, texts, autotexts = ax1.pie(mkt_pcts, labels=mkt_labels, autopct='%1.0f%%',
                                    colors=mkt_colors, startangle=90,
                                    pctdistance=0.75, textprops={'fontsize': 9})
# Make it a donut
centre_circle = plt.Circle((0, 0), 0.50, fc='white')
ax1.add_artist(centre_circle)
ax1.text(0, 0, 'Marketing\nBudget\nAllocation', ha='center', va='center',
         fontsize=11, fontweight='bold', color='#333')
for t in autotexts:
    t.set_fontweight('bold')
    t.set_fontsize(11)
ax1.set_title('Recommended Marketing Mix', fontsize=13, fontweight='bold', pad=15)

# Pricing Tier Split
ax2 = axes[1]
tier_names = ['Mass\n(Rs 199-399)', 'Mid\n(Rs 399-799)', 'Premium\n(Rs 799-1,499)']
tier_shares = [45, 40, 15]
tier_colors = ['#44BBA4', '#2E86AB', '#A23B72']

bars = ax2.bar(tier_names, tier_shares, color=tier_colors, width=0.5, edgecolor='white', linewidth=2)
for bar, share in zip(bars, tier_shares):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{share}%', ha='center', fontsize=14, fontweight='bold')
ax2.set_ylabel('Revenue Share (%)', fontsize=12, fontweight='bold')
ax2.set_title('Revenue Distribution by Pricing Tier', fontsize=13, fontweight='bold', pad=15)
ax2.set_ylim(0, 60)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

fig.suptitle('Go-to-Market Strategy', fontsize=16, fontweight='bold', y=1.02)
fig.tight_layout()
save_fig(fig, '11_gtm_strategy.png')


print(f"\n{'='*60}")
print(f"ALL {11} CHARTS GENERATED SUCCESSFULLY")
print(f"Output directory: {OUTPUTS_DIR}/")
print(f"{'='*60}")