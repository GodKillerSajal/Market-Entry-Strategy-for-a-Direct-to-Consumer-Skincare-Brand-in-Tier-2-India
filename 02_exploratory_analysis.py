"""
Project 1: Market-Entry Strategy for a D2C Skincare Brand in Tier-2 India
Script 02: Exploratory Data Analysis (EDA)
===============================================================================
Analyzes the consumer survey data to understand distributions, patterns,
correlations, and key demographic differences across Tier-2 cities.
"""

import numpy as np
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# Load data
df = pd.read_csv(os.path.join(RAW_DIR, "consumer_survey_data.csv"))

results = {}

# =============================================================================
# 1. DEMOGRAPHIC OVERVIEW
# =============================================================================

demo_summary = {
    "Total_Responses": len(df),
    "Cities_Covered": df["city"].nunique(),
    "Avg_Age": round(df["age"].mean(), 1),
    "Female_Pct": round((df["gender"] == "Female").mean() * 100, 1),
    "D2C_Awareness_Pct": round((df["awareness_of_d2c_brands"] == "Yes").mean() * 100, 1),
}
results["demographic_summary"] = demo_summary

# City-wise breakdown
city_stats = df.groupby("city").agg(
    Respondents=("respondent_id", "count"),
    Avg_Age=("age", "mean"),
    Avg_Spend=("current_skincare_spend_monthly", "mean"),
    Avg_Price_Sensitivity=("price_sensitivity", "mean"),
    Avg_Natural_Preference=("natural_preference", "mean"),
    D2C_Awareness_Pct=("awareness_of_d2c_brands", lambda x: (x == "Yes").mean() * 100),
    Online_Channel_Pct=("preferred_channel", lambda x: (x == "Online").mean() * 100),
    Avg_Satisfaction=("satisfaction_current_products", "mean"),
).round(2)
results["city_stats"] = city_stats.to_dict(orient="index")

print("=== DEMOGRAPHIC OVERVIEW ===")
print(f"  Total Responses: {demo_summary['Total_Responses']:,}")
print(f"  Cities: {demo_summary['Cities_Covered']}")
print(f"  Avg Age: {demo_summary['Avg_Age']}")
print(f"  Female %: {demo_summary['Female_Pct']}%")
print(f"  D2C Awareness: {demo_summary['D2C_Awareness_Pct']}%")

# =============================================================================
# 2. SPENDING ANALYSIS
# =============================================================================

# Income bracket vs. spend
income_spend = df.groupby("income_bracket")["current_skincare_spend_monthly"].agg(
    ["mean", "median", "std", "min", "max"]
).round(2)
results["income_spend"] = income_spend.to_dict(orient="index")

# Age group vs. spend
age_spend = df.groupby("age_group")["current_skincare_spend_monthly"].agg(
    ["mean", "median", "count"]
).round(2)
results["age_spend"] = age_spend.to_dict(orient="index")

# Channel preference distribution
channel_dist = df["preferred_channel"].value_counts(normalize=True).round(3) * 100
results["channel_distribution"] = channel_dist.to_dict()

print("\n=== SPENDING ANALYSIS ===")
print(f"  Overall Avg Monthly Spend: Rs {df['current_skincare_spend_monthly'].mean():.0f}")
print(f"  Median Monthly Spend: Rs {df['current_skincare_spend_monthly'].median():.0f}")
print(f"  Channel Preference: {dict(channel_dist)}")

# =============================================================================
# 3. PRICE SENSITIVITY ANALYSIS
# =============================================================================

price_by_income = df.groupby("income_bracket")["price_sensitivity"].mean().round(2)
price_by_age = df.groupby("age_group")["price_sensitivity"].mean().round(2)
price_by_city = df.groupby("city")["price_sensitivity"].mean().round(2).sort_values(ascending=False)

results["price_sensitivity"] = {
    "by_income": price_by_income.to_dict(),
    "by_age": price_by_age.to_dict(),
    "by_city": price_by_city.to_dict(),
    "overall_avg": round(df["price_sensitivity"].mean(), 2),
}

print("\n=== PRICE SENSITIVITY ===")
print(f"  Overall Avg: {df['price_sensitivity'].mean():.2f}/10")
print(f"  By Income: {dict(price_by_income)}")

# =============================================================================
# 4. NATURAL / CLEAN BEAUTY PREFERENCE
# =============================================================================

natural_by_city = df.groupby("city")["natural_preference"].mean().round(2).sort_values(ascending=False)
natural_by_age = df.groupby("age_group")["natural_preference"].mean().round(2)
natural_vs_chemical = df["natural_preference"].describe()

results["natural_preference"] = {
    "by_city": natural_by_city.to_dict(),
    "by_age": natural_by_age.to_dict(),
    "stats": {
        "mean": round(natural_vs_chemical["mean"], 2),
        "std": round(natural_vs_chemical["std"], 2),
        "min": round(natural_vs_chemical["min"], 2),
        "max": round(natural_vs_chemical["max"], 2),
    },
    "high_preference_pct": round((df["natural_preference"] >= 7).mean() * 100, 1),
}

print("\n=== NATURAL PREFERENCE ===")
print(f"  Avg Score: {df['natural_preference'].mean():.2f}/10")
print(f"  High Preference (>=7): {results['natural_preference']['high_preference_pct']}%")
print(f"  Top Cities: {dict(natural_by_city.head(3))}")

# =============================================================================
# 5. CHANNEL PREFERENCE BY AGE GROUP
# =============================================================================

channel_by_age = pd.crosstab(df["age_group"], df["preferred_channel"], normalize="index").round(3) * 100
results["channel_by_age"] = channel_by_age.to_dict(orient="index")

print("\n=== CHANNEL BY AGE GROUP ===")
print(channel_by_age.to_string())

# =============================================================================
# 6. PRODUCT CATEGORY INTEREST ANALYSIS
# =============================================================================

# Parse multi-category column
from collections import Counter

all_categories = []
for cats in df["product_categories_interest"]:
    all_categories.extend([c.strip() for c in cats.split(",")])

cat_counts = Counter(all_categories)
cat_df = pd.DataFrame(cat_counts.most_common(), columns=["Category", "Mentions"]).set_index("Category")
cat_df["Pct"] = (cat_df["Mentions"] / len(df) * 100).round(1)
cat_df = cat_df.sort_values("Mentions", ascending=False)
results["category_interest"] = cat_df.to_dict(orient="index")

print("\n=== TOP PRODUCT CATEGORIES ===")
print(cat_df.head(8).to_string())

# =============================================================================
# 7. TOP SKIN CONCERNS
# =============================================================================

all_concerns = []
for concerns in df["top_concerns"]:
    all_concerns.extend([c.strip() for c in concerns.split(",")])

concern_counts = Counter(all_concerns)
concern_df = pd.DataFrame(concern_counts.most_common(), columns=["Concern", "Mentions"]).set_index("Concern")
concern_df["Pct"] = (concern_df["Mentions"] / len(df) * 100).round(1)

results["top_concerns"] = concern_df.to_dict(orient="index")

print("\n=== TOP SKIN CONCERNS ===")
print(concern_df.to_string())

# =============================================================================
# 8. CORRELATION ANALYSIS
# =============================================================================

numeric_cols = ["age", "current_skincare_spend_monthly", "brand_loyalty_score",
                "price_sensitivity", "natural_preference", "purchase_frequency",
                "willingness_to_try_new_brand", "social_media_influence",
                "satisfaction_current_products"]

corr_matrix = df[numeric_cols].corr().round(3)
results["correlations"] = corr_matrix.to_dict(orient="index")

# Key correlations
key_corrs = {
    "age_vs_spend": corr_matrix.loc["age", "current_skincare_spend_monthly"],
    "price_sens_vs_income_spend": corr_matrix.loc["price_sensitivity", "current_skincare_spend_monthly"],
    "natural_vs_satisfaction": corr_matrix.loc["natural_preference", "satisfaction_current_products"],
    "social_media_vs_willingness": corr_matrix.loc["social_media_influence", "willingness_to_try_new_brand"],
    "loyalty_vs_willingness": corr_matrix.loc["brand_loyalty_score", "willingness_to_try_new_brand"],
}

print("\n=== KEY CORRELATIONS ===")
for k, v in key_corrs.items():
    print(f"  {k}: {v:.3f}")

# =============================================================================
# 9. DEMAND GAP ANALYSIS (high interest + low satisfaction)
# =============================================================================

# Calculate category-level satisfaction gap
# For each category mentioned, what's the average satisfaction?
cat_satisfaction = {}
for cat in cat_df.index[:8]:  # Top 8 categories
    mask = df["product_categories_interest"].str.contains(cat, na=False)
    cat_satisfaction[cat] = {
        "interest_pct": round(cat_df.loc[cat, "Pct"], 1),
        "avg_satisfaction": round(df.loc[mask, "satisfaction_current_products"].mean(), 2),
        "avg_natural_pref": round(df.loc[mask, "natural_preference"].mean(), 2),
    }

# Calculate a "gap score" = high interest + low satisfaction = opportunity
gap_df = pd.DataFrame(cat_satisfaction).T
gap_df["gap_score"] = gap_df["interest_pct"] * (10 - gap_df["avg_satisfaction"]) / 10
gap_df = gap_df.sort_values("gap_score", ascending=False)
results["demand_gaps"] = gap_df.to_dict(orient="index")

print("\n=== DEMAND GAP ANALYSIS ===")
print("(Higher gap score = bigger opportunity)")
print(gap_df.round(2).to_string())

# =============================================================================
# 10. SAVE ALL RESULTS
# =============================================================================

# Save key dataframes for visualization
city_stats.to_csv(os.path.join(PROCESSED_DIR, "city_wise_stats.csv"))
cat_df.to_csv(os.path.join(PROCESSED_DIR, "category_interest.csv"))
concern_df.to_csv(os.path.join(PROCESSED_DIR, "skin_concerns.csv"))
corr_matrix.to_csv(os.path.join(PROCESSED_DIR, "correlation_matrix.csv"))
gap_df.to_csv(os.path.join(PROCESSED_DIR, "demand_gaps.csv"))
channel_by_age.to_csv(os.path.join(PROCESSED_DIR, "channel_by_age.csv"))

# Save comprehensive results as JSON
# Convert non-serializable types
def convert(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="index")
    return obj

with open(os.path.join(PROCESSED_DIR, "eda_results.json"), "w") as f:
    json.dump(results, f, default=convert, indent=2)

print("\n" + "=" * 60)
print("EXPLORATORY DATA ANALYSIS COMPLETE")
print(f"All results saved to {PROCESSED_DIR}/")
print("=" * 60)