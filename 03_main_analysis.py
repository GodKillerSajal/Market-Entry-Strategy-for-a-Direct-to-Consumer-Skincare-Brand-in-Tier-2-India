"""
Project 1: Market-Entry Strategy for a D2C Skincare Brand in Tier-2 India
Script 03: Main Analysis — Demand Gaps, Competitive Positioning, STP Framework
===============================================================================
"""

import numpy as np
import pandas as pd
import json
import os
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Load data
df = pd.read_csv(os.path.join(RAW_DIR, "consumer_survey_data.csv"))
comp_df = pd.read_csv(os.path.join(PROCESSED_DIR, "competitive_landscape.csv"))
gap_df = pd.read_csv(os.path.join(PROCESSED_DIR, "demand_gaps.csv"), index_col=0)

# =============================================================================
# 1. DETAILED DEMAND GAP ANALYSIS
# =============================================================================

print("=" * 60)
print("1. DETAILED DEMAND GAP ANALYSIS")
print("=" * 60)

# Parse product categories for each respondent and find unsatisfied categories
all_categories = ["Face Wash", "Moisturizer", "Serum", "Sunscreen",
                  "Face Mask", "Cleanser", "Toner", "Night Cream",
                  "Anti-Pollution", "Anti-Aging", "Herbal/Ubtan", "Body Lotion"]

category_metrics = []
for cat in all_categories:
    mask = df["product_categories_interest"].str.contains(cat, na=False)
    n_interested = mask.sum()
    if n_interested == 0:
        continue
    interested_df = df[mask]
    
    # Average satisfaction among those interested
    avg_sat = interested_df["satisfaction_current_products"].mean()
    
    # % with low satisfaction (<=5) among those interested
    low_sat_pct = (interested_df["satisfaction_current_products"] <= 5).mean() * 100
    
    # Average natural preference among those interested
    avg_natural = interested_df["natural_preference"].mean()
    
    # Average willingness to try new brand
    avg_willingness = interested_df["willingness_to_try_new_brand"].mean()
    
    # Price sensitivity
    avg_price_sens = interested_df["price_sensitivity"].mean()
    
    # Interest rate
    interest_pct = n_interested / len(df) * 100
    
    # Composite opportunity score
    # High interest + low satisfaction + high willingness = big opportunity
    opportunity_score = (interest_pct / 100) * ((10 - avg_sat) / 10) * (avg_willingness / 10) * 100
    
    category_metrics.append({
        "Category": cat,
        "Interest_Pct": round(interest_pct, 1),
        "Avg_Satisfaction": round(avg_sat, 2),
        "Low_Satisfaction_Pct": round(low_sat_pct, 1),
        "Avg_Natural_Preference": round(avg_natural, 2),
        "Avg_Willingness_To_Try": round(avg_willingness, 2),
        "Avg_Price_Sensitivity": round(avg_price_sens, 2),
        "Opportunity_Score": round(opportunity_score, 2),
    })

demand_gap_detail = pd.DataFrame(category_metrics).sort_values("Opportunity_Score", ascending=False)
demand_gap_detail.to_csv(os.path.join(PROCESSED_DIR, "demand_gap_detail.csv"), index=False)
print(demand_gap_detail.to_string(index=False))

# =============================================================================
# 2. COMPETITIVE POSITIONING MAP DATA
# =============================================================================

print("\n" + "=" * 60)
print("2. COMPETITIVE POSITIONING ANALYSIS")
print("=" * 60)

# Price positioning score (1-10 scale: 1=cheapest, 10=most expensive)
price_midpoints = {
    "Mass": 3.0,
    "Mass-Premium": 5.5,
    "Mid-Premium": 7.0,
    "Premium": 8.5,
}
comp_df["Price_Score"] = comp_df["Pricing_Positioning"].map(price_midpoints)
# Add small random noise for spread
comp_df["Price_Score"] = comp_df["Price_Score"] + np.random.uniform(-0.3, 0.3, len(comp_df))

# Natural Score already exists (1=chemical, 10=fully natural)
# Calculate market presence score (funding + followers)
comp_df["Funding_Cr"] = comp_df["Funding_Raised_Cr"].astype(float)
comp_df["Market_Presence"] = (
    comp_df["Funding_Cr"] / comp_df["Funding_Cr"].max() * 0.6 +
    comp_df["Instagram_Followers_M"] / comp_df["Instagram_Followers_M"].max() * 0.4
).round(2)

# White space analysis
# Quadrant analysis: Price (low-high) x Natural (low-high)
median_price = comp_df["Price_Score"].median()
median_natural = comp_df["Natural_Score"].median()

comp_df["Quadrant"] = comp_df.apply(
    lambda r: "High Price + High Natural" if r["Price_Score"] >= median_price and r["Natural_Score"] >= median_natural
    else "Low Price + High Natural" if r["Price_Score"] < median_price and r["Natural_Score"] >= median_natural
    else "High Price + Low Natural" if r["Price_Score"] >= median_price and r["Natural_Score"] < median_natural
    else "Low Price + Low Natural", axis=1
)

quadrant_counts = comp_df["Quadrant"].value_counts()
print("\nCompetitive Quadrant Distribution:")
print(quadrant_counts.to_string())

# Identify white space
white_space_quadrants = [q for q, c in quadrant_counts.items() if c <= 2]
print(f"\nWhite Space Opportunities (quadrants with <=2 competitors):")
for q in white_space_quadrants:
    print(f"  - {q}: {quadrant_counts[q]} competitor(s)")

comp_df.to_csv(os.path.join(PROCESSED_DIR, "competitive_positioning.csv"), index=False)

# =============================================================================
# 3. STP FRAMEWORK — SEGMENTATION, TARGETING, POSITIONING
# =============================================================================

print("\n" + "=" * 60)
print("3. STP FRAMEWORK — TARGET SEGMENTS")
print("=" * 60)

# Create segment variables
# Segment based on: willingness to try, natural preference, spend, age
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

segment_features = df[["willingness_to_try_new_brand", "natural_preference",
                       "current_skincare_spend_monthly", "age",
                       "price_sensitivity", "social_media_influence"]].copy()

scaler = StandardScaler()
scaled_features = scaler.fit_transform(segment_features)

# Run K-Means with k=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["segment"] = kmeans.fit_predict(scaled_features)

# Profile each segment
segments = {}
for seg in sorted(df["segment"].unique()):
    seg_data = df[df["segment"] == seg]
    
    # Most common concerns
    all_concerns_seg = []
    for c in seg_data["top_concerns"]:
        all_concerns_seg.extend([x.strip() for x in c.split(",")])
    top_concerns_seg = Counter(all_concerns_seg).most_common(3)
    
    # Most common categories
    all_cats_seg = []
    for c in seg_data["product_categories_interest"]:
        all_cats_seg.extend([x.strip() for x in c.split(",")])
    top_cats_seg = Counter(all_cats_seg).most_common(3)
    
    # Channel preference
    top_channel = seg_data["preferred_channel"].mode().iloc[0]
    
    seg_name = f"Segment_{seg}"
    segments[seg_name] = {
        "size": len(seg_data),
        "size_pct": round(len(seg_data) / len(df) * 100, 1),
        "avg_age": round(seg_data["age"].mean(), 1),
        "avg_spend": round(seg_data["current_skincare_spend_monthly"].mean(), 0),
        "avg_natural_pref": round(seg_data["natural_preference"].mean(), 2),
        "avg_price_sens": round(seg_data["price_sensitivity"].mean(), 2),
        "avg_willingness": round(seg_data["willingness_to_try_new_brand"].mean(), 2),
        "avg_social_media": round(seg_data["social_media_influence"].mean(), 2),
        "d2c_awareness_pct": round((seg_data["awareness_of_d2c_brands"] == "Yes").mean() * 100, 1),
        "top_channel": top_channel,
        "top_concerns": [c[0] for c in top_concerns_seg],
        "top_categories": [c[0] for c in top_cats_seg],
        "top_income_bracket": seg_data["income_bracket"].mode().iloc[0],
    }

# Name the segments based on characteristics (ensure unique names)
used_names = set()
seg_names = {}
for seg_id, seg_data in segments.items():
    if seg_data["avg_spend"] >= 1500 and seg_data["avg_natural_pref"] >= 6.5:
        candidate = "Conscious Premium Spenders"
    elif seg_data["avg_willingness"] >= 6.5 and seg_data["avg_social_media"] >= 6.5:
        candidate = "Digital-First Experimenters"
    elif seg_data["avg_price_sens"] >= 6.5 and seg_data["avg_spend"] <= 800:
        candidate = "Value-Conscious Seekers"
    else:
        candidate = "Mainstream Urban Women"
    # De-duplicate by appending suffix
    if candidate in used_names:
        candidate = candidate + " (B)"
    used_names.add(candidate)
    seg_names[seg_id] = candidate

for seg_id, name in seg_names.items():
    segments[seg_id]["name"] = name
    print(f"\n  {name} ({seg_id}):")
    print(f"    Size: {segments[seg_id]['size']} ({segments[seg_id]['size_pct']}%)")
    print(f"    Avg Age: {segments[seg_id]['avg_age']}, Avg Spend: Rs {segments[seg_id]['avg_spend']}/month")
    print(f"    Natural Pref: {segments[seg_id]['avg_natural_pref']}, Price Sens: {segments[seg_id]['avg_price_sens']}")
    print(f"    Top Concerns: {segments[seg_id]['top_concerns']}")
    print(f"    Top Categories: {segments[seg_id]['top_categories']}")

# Save segment data
seg_df = df.copy()
seg_df["segment_name"] = seg_df["segment"].map({int(k.split("_")[1]): v["name"] for k, v in segments.items()})
seg_df.to_csv(os.path.join(PROCESSED_DIR, "segmented_survey_data.csv"), index=False)

segments_summary = pd.DataFrame(segments).T
segments_summary.to_csv(os.path.join(PROCESSED_DIR, "segment_profiles.csv"))

# =============================================================================
# 4. GO-TO-MARKET STRATEGY RECOMMENDATIONS
# =============================================================================

print("\n" + "=" * 60)
print("4. GO-TO-MARKET STRATEGY RECOMMENDATIONS")
print("=" * 60)

# Pricing tier recommendation based on price sensitivity distribution
price_sens_dist = df["price_sensitivity"].describe()
high_sens_pct = (df["price_sensitivity"] >= 7).mean() * 100
mid_sens_pct = ((df["price_sensitivity"] >= 4) & (df["price_sensitivity"] < 7)).mean() * 100
low_sens_pct = (df["price_sensitivity"] < 4).mean() * 100

pricing_recommendations = {
    "Mass_Tier": {
        "price_range": "Rs 199-399",
        "target_segment": "Value-Conscious Seekers, early adopters",
        "rationale": f"{high_sens_pct:.0f}% of respondents show high price sensitivity (>=7/10). "
                     f"A mass tier at Rs 199-399 captures volume in Tier-2 where average monthly "
                     f"spend is Rs {df['current_skincare_spend_monthly'].mean():.0f}.",
        "products": ["Face Wash", "Cleanser", "Body Lotion"],
        "estimated_share": "45% of revenue",
    },
    "Mid_Tier": {
        "price_range": "Rs 399-799",
        "target_segment": "Digital-First Experimenters, Mainstream Urban Women",
        "rationale": f"{mid_sens_pct:.0f}% have moderate price sensitivity. The Rs 399-799 "
                     f"sweet spot aligns with average monthly spend and captures consumers "
                     f"trading up from mass brands to D2C.",
        "products": ["Serum", "Moisturizer", "Sunscreen", "Face Mask"],
        "estimated_share": "40% of revenue",
    },
    "Premium_Tier": {
        "price_range": "Rs 799-1499",
        "target_segment": "Conscious Premium Spenders",
        "rationale": f"{low_sens_pct:.0f}% are price-insensitive and willing to pay for quality. "
                     f"Premium natural/anti-pollution products at Rs 799-1499 capture the "
                     f"high-LTV segment with avg spend Rs 1,500+/month.",
        "products": ["Anti-Pollution Serum", "Night Cream", "Vitamin C Serum"],
        "estimated_share": "15% of revenue",
    },
}

print("\nPricing Tiers:")
for tier, details in pricing_recommendations.items():
    print(f"\n  {tier} ({details['price_range']}):")
    print(f"    Target: {details['target_segment']}")
    print(f"    Products: {details['products']}")
    print(f"    Revenue Share: {details['estimated_share']}")

# Channel strategy
online_pct = (df["preferred_channel"] == "Online").mean() * 100
both_pct = (df["preferred_channel"] == "Both").mean() * 100
offline_pct = (df["preferred_channel"] == "Offline").mean() * 100

channel_strategy = {
    "Phase_1_Online_First": {
        "channels": ["Own Website (D2C)", "Nykaa", "Myntra", "Amazon"],
        "rationale": f"{online_pct:.0f}% prefer online. Own site for margins, marketplaces for discovery.",
        "budget_allocation": "70% of distribution budget",
    },
    "Phase_2_Selective_Offline": {
        "channels": ["Premium beauty stores in Jaipur, Lucknow, Indore", "Pharmacy chains"],
        "rationale": f"{both_pct:.0f}% use both channels. Offline presence builds trust in Tier-2.",
        "budget_allocation": "30% of distribution budget",
    },
}

# Marketing mix
marketing_mix = {
    "Instagram_YouTube_Influencers": {
        "budget_pct": 40,
        "rationale": f"Avg social media influence score: {df['social_media_influence'].mean():.1f}/10. "
                     f"Younger demographics (18-29) heavily influenced by beauty creators.",
    },
    "Google_Search_Ads": {
        "budget_pct": 25,
        "rationale": "Capture high-intent searches for 'natural face wash', 'anti-pollution serum', etc.",
    },
    "Sample_Boxes": {
        "budget_pct": 20,
        "rationale": f"Low D2C awareness ({(df['awareness_of_d2c_brands']=='Yes').mean()*100:.0f}% in sample) "
                     f"makes sampling critical for trial. Target: Digital-First Experimenters segment.",
    },
    "Offline_Activations": {
        "budget_pct": 15,
        "rationale": "Pop-ups in college fests, mall activations in top 3 Tier-2 cities for brand discovery.",
    },
}

print("\nMarketing Mix:")
for channel, details in marketing_mix.items():
    print(f"  {channel.replace('_', ' ')}: {details['budget_pct']}% budget")

# =============================================================================
# 5. 3-YEAR FINANCIAL PROJECTION (HIGH-LEVEL)
# =============================================================================

print("\n" + "=" * 60)
print("5. 3-YEAR FINANCIAL PROJECTION SUMMARY")
print("=" * 60)

financials = {
    "Year": [1, 2, 3],
    "Revenue_Cr": [2.0, 8.5, 22.0],
    "COGS_Pct": [60, 55, 50],
    "Gross_Margin_Pct": [40, 45, 50],
    "Marketing_Pct": [30, 25, 20],
    "OpEx_Pct": [18, 14, 12],
    "EBITDA_Pct": [-8, 6, 18],
    "Customers": [8000, 35000, 90000],
    "AOV_INR": [250, 280, 310],
    "CAC_INR": [350, 280, 220],
    "LTV_INR": [750, 1050, 1350],
}

fin_df = pd.DataFrame(financials)
fin_df["Gross_Profit_Cr"] = (fin_df["Revenue_Cr"] * fin_df["Gross_Margin_Pct"] / 100).round(2)
fin_df["Marketing_Cr"] = (fin_df["Revenue_Cr"] * fin_df["Marketing_Pct"] / 100).round(2)
fin_df["OpEx_Cr"] = (fin_df["Revenue_Cr"] * fin_df["OpEx_Pct"] / 100).round(2)
fin_df["EBITDA_Cr"] = (fin_df["Revenue_Cr"] * fin_df["EBITDA_Pct"] / 100).round(2)
fin_df["LTV_CAC_Ratio"] = (fin_df["LTV_INR"] / fin_df["CAC_INR"]).round(2)

print(fin_df[["Year", "Revenue_Cr", "Gross_Profit_Cr", "Marketing_Cr", "EBITDA_Cr", 
               "Customers", "AOV_INR", "CAC_INR", "LTV_CAC_Ratio"]].to_string(index=False))

# Break-even calculation
# Month-by-month for first 24 months (to capture break-even at ~month 14-18)
# Year 1: ramping up; Year 2: scaling
y1_revenue = [5, 8, 12, 15, 18, 22, 26, 30, 34, 38, 42, 50]
y2_revenue = [55, 62, 68, 75, 82, 90, 98, 106, 115, 125, 135, 145]
all_revenue = y1_revenue + y2_revenue

# Margins improve as we scale (COGS drops, marketing becomes efficient)
cogs_pcts = [0.62]*6 + [0.60]*6 + [0.57]*6 + [0.55]*6
mkt_pcts  = [0.32]*6 + [0.28]*6 + [0.25]*6 + [0.22]*6
opex_pcts = [0.20]*6 + [0.17]*6 + [0.14]*6 + [0.13]*6

months_all = pd.DataFrame({
    "Month": range(1, 25),
    "Revenue_Lakhs": all_revenue,
})
months_all["COGS_Lakhs"] = (months_all["Revenue_Lakhs"] * cogs_pcts).round(2)
months_all["Marketing_Lakhs"] = (months_all["Revenue_Lakhs"] * mkt_pcts).round(2)
months_all["OpEx_Lakhs"] = (months_all["Revenue_Lakhs"] * opex_pcts).round(2)
months_all["EBITDA_Lakhs"] = (months_all["Revenue_Lakhs"] - months_all["COGS_Lakhs"]
                             - months_all["Marketing_Lakhs"] - months_all["OpEx_Lakhs"]).round(2)
months_all["Cumulative_EBITDA_Lakhs"] = months_all["EBITDA_Lakhs"].cumsum().round(2)

# Split back into year 1 and year 2 for display
months_y1 = months_all[months_all["Month"] <= 12].copy()
months_y2 = months_all[months_all["Month"] > 12].copy()

breakeven_month = None
for _, row in months_all.iterrows():
    if row["Cumulative_EBITDA_Lakhs"] >= 0:
        breakeven_month = int(row["Month"])
        break

print(f"\nBreak-even Analysis:")
print(f"  Break-even at Month: {breakeven_month if breakeven_month else 'Not in 24 months'}")
print(f"  Y1 Total Revenue: Rs {months_y1['Revenue_Lakhs'].sum()} Lakhs")
print(f"  Y1 Total EBITDA: Rs {months_y1['EBITDA_Lakhs'].sum():.1f} Lakhs")
print(f"  Y2 Total Revenue: Rs {months_y2['Revenue_Lakhs'].sum()} Lakhs")

# Save financials
fin_df.to_csv(os.path.join(PROCESSED_DIR, "financial_projections_3yr.csv"), index=False)
months_all.to_csv(os.path.join(PROCESSED_DIR, "monthly_breakdown_24m.csv"), index=False)
months_y1.to_csv(os.path.join(PROCESSED_DIR, "monthly_breakdown_y1.csv"), index=False)

# Save comprehensive recommendations
recommendations = {
    "pricing_tiers": pricing_recommendations,
    "channel_strategy": channel_strategy,
    "marketing_mix": marketing_mix,
    "break_even_month": breakeven_month,
    "price_sensitivity_distribution": {
        "high_sensitivity_pct": round(high_sens_pct, 1),
        "moderate_sensitivity_pct": round(mid_sens_pct, 1),
        "low_sensitivity_pct": round(low_sens_pct, 1),
    },
    "channel_preference": {
        "online_pct": round(online_pct, 1),
        "both_pct": round(both_pct, 1),
        "offline_pct": round(offline_pct, 1),
    },
}

with open(os.path.join(PROCESSED_DIR, "gtm_recommendations.json"), "w") as f:
    json.dump(recommendations, f, indent=2, default=str)

print("\n" + "=" * 60)
print("MAIN ANALYSIS COMPLETE")
print(f"All outputs saved to {PROCESSED_DIR}/")
print("=" * 60)