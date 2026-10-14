"""
Project 1: Market-Entry Strategy for a D2C Skincare Brand in Tier-2 India
Script 01: Data Preparation — Market Sizing + Synthetic Survey Data Generation
===============================================================================
Generates:
  1. Market sizing analysis (top-down and bottom-up) saved to CSV
  2. Synthetic consumer survey dataset (5,000+ responses across 8 Tier-2 cities)
  3. Competitive landscape dataset for 8 D2C skincare brands
"""

import numpy as np
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

np.random.seed(42)

# =============================================================================
# 1. MARKET SIZING ANALYSIS
# =============================================================================

# --- Top-Down Approach ---
# India skincare TAM: USD 9.06B (2025), projected USD 18.38B by 2034, CAGR 7.2%
# Source: IMARC Group, Research & Markets
# USD to INR rate ~83.5

usd_inr = 83.5
india_skincare_tam_usd = 9.06  # billion USD
india_skincare_tam_inr = india_skincare_tam_usd * usd_inr * 100  # Convert to Crore (1B USD = 8350 Cr INR)

# India D2C beauty market: Rs 6.6 lakh crore, growing at 36.4% CAGR (2025-2032)
# D2C is a subset of the broader beauty market
d2c_beauty_market_cr = 660000  # Rs in crore (6.6 lakh crore)

# Skincare is ~30% of the beauty & personal care market
skincare_share_of_beauty = 0.30
d2c_skincare_market_cr = d2c_beauty_market_cr * skincare_share_of_beauty  # ~1,98,000 Cr

# Online channel is ~25% of D2C beauty
online_channel_share = 0.25
online_d2c_skincare_cr = d2c_skincare_market_cr * online_channel_share  # ~49,500 Cr

# Tier-2 cities contribute ~35% of D2C revenue
tier2_revenue_share = 0.35
sam_topdown_cr = online_d2c_skincare_cr * tier2_revenue_share  # ~17,325 Cr
sam_topdown_usd = sam_topdown_cr / (usd_inr * 100)  # Convert Cr to billion USD

# Narrow to addressable new-entrant share (~5% of SAM in year 1)
som_topdown_cr = sam_topdown_cr * 0.05

# --- Bottom-Up Approach ---
# Target demographic: Women 18-35 in Tier-2 cities
# 8 sample Tier-2 cities: Indore, Bhopal, Jaipur, Lucknow, Coimbatore, Kochi, Vizag, Nagpur
# Total Tier-2 city women 18-35 population estimate: ~40M

tier2_cities = {
    "Indore": {"pop_lakhs": 32, "urban_pct": 0.65},
    "Bhopal": {"pop_lakhs": 28, "urban_pct": 0.62},
    "Jaipur": {"pop_lakhs": 42, "urban_pct": 0.60},
    "Lucknow": {"pop_lakhs": 45, "urban_pct": 0.58},
    "Coimbatore": {"pop_lakhs": 25, "urban_pct": 0.70},
    "Kochi": {"pop_lakhs": 22, "urban_pct": 0.68},
    "Vizag": {"pop_lakhs": 20, "urban_pct": 0.60},
    "Nagpur": {"pop_lakhs": 29, "urban_pct": 0.64},
}

# Women 18-35 ~20% of city population, urban area
# Penetration rate for D2C skincare ~15% of target demo
# Avg annual spend on skincare ~Rs 2,500
avg_annual_spend = 2500
penetration_rate = 0.15
women_18_35_pct = 0.20

total_target_pop = 0
for city, data in tier2_cities.items():
    urban_pop = data["pop_lakhs"] * 100000 * data["urban_pct"]
    target_pop = urban_pop * women_18_35_pct
    total_target_pop += target_pop

sam_bottomup_cr = (total_target_pop * penetration_rate * avg_annual_spend) / 10000000  # Convert to Cr
sam_bottomup_usd = sam_bottomup_cr / (usd_inr * 100)

# Summary
market_sizing = {
    "Approach": ["Top-Down", "Bottom-Up"],
    "SAM_INR_Crore": [round(sam_topdown_cr, 0), round(sam_bottomup_cr, 0)],
    "SAM_USD_Billion": [round(sam_topdown_usd, 2), round(sam_bottomup_usd, 2)],
    "Key_Assumptions": [
        "D2C beauty Rs 6.6L Cr, skincare 30%, online 25%, Tier-2 35%",
        f"8 cities, target pop {total_target_pop/1e6:.1f}M, penetration 15%, avg spend Rs 2,500"
    ]
}
market_sizing_df = pd.DataFrame(market_sizing)

# Save intermediate sizing details
sizing_details = {
    "india_skincare_tam_usd_billion": india_skincare_tam_usd,
    "india_skincare_tam_inr_crore": round(india_skincare_tam_inr, 0),
    "d2c_beauty_market_crore": d2c_beauty_market_cr,
    "d2c_skincare_market_crore": round(d2c_skincare_market_cr, 0),
    "online_d2c_skincare_crore": round(online_d2c_skincare_cr, 0),
    "sam_topdown_crore": round(sam_topdown_cr, 0),
    "sam_bottomup_crore": round(sam_bottomup_cr, 0),
    "som_topdown_crore": round(som_topdown_cr, 0),
    "total_target_pop_millions": round(total_target_pop / 1e6, 2),
    "avg_annual_spend_inr": avg_annual_spend,
    "penetration_rate": penetration_rate,
}

market_sizing_df.to_csv(os.path.join(PROCESSED_DIR, "market_sizing_summary.csv"), index=False)
with open(os.path.join(PROCESSED_DIR, "market_sizing_details.json"), "w") as f:
    json.dump(sizing_details, f, indent=2)

print(f"Market Sizing Complete:")
print(f"  Top-Down SAM: Rs {sam_topdown_cr:,.0f} Cr (USD {sam_topdown_usd:.2f}B)")
print(f"  Bottom-Up SAM: Rs {sam_bottomup_cr:,.0f} Cr (USD {sam_bottomup_usd:.2f}B)")
print(f"  Target Population: {total_target_pop/1e6:.2f}M women 18-35")


# =============================================================================
# 2. SYNTHETIC CONSUMER SURVEY DATA (5,000+ responses)
# =============================================================================

N = 5500  # Number of survey responses

cities = list(tier2_cities.keys())
city_weights = np.array([tier2_cities[c]["pop_lakhs"] for c in cities])
city_weights = city_weights / city_weights.sum()

age_groups = {
    "18-24": (18, 24),
    "25-29": (25, 29),
    "30-35": (30, 35),
}
age_probs = [0.40, 0.38, 0.22]  # Younger demographics more responsive to surveys

income_brackets = ["<15K", "15K-25K", "25K-50K", "50K-75K", ">75K"]
# Tier-2 income distribution — skewed towards lower-mid
income_probs = [0.15, 0.30, 0.32, 0.15, 0.08]

product_categories = [
    "Face Wash", "Moisturizer", "Serum", "Sunscreen",
    "Face Mask", "Cleanser", "Toner", "Night Cream",
    "Anti-Pollution", "Anti-Aging", "Herbal/Ubtan", "Body Lotion"
]

top_concerns_options = ["Acne", "Pollution Damage", "Aging", "Dryness", 
                        "Uneven Skin Tone", "Oiliness", "Dark Circles", "Pigmentation"]

# Generate base variables
data = {
    "respondent_id": range(1, N + 1),
    "city": np.random.choice(cities, size=N, p=city_weights),
    "age": np.concatenate([
        np.random.randint(18, 25, size=int(N * age_probs[0])),
        np.random.randint(25, 30, size=int(N * age_probs[1])),
        np.random.randint(30, 36, size=N - int(N * age_probs[0]) - int(N * age_probs[1]))
    ]),
    "gender": np.random.choice(["Female", "Male", "Non-Binary"], size=N, p=[0.88, 0.10, 0.02]),
    "income_bracket": np.random.choice(income_brackets, size=N, p=income_probs),
}

df = pd.DataFrame(data)

# --- Derived variables based on demographics ---

# Skincare spend monthly (INR) — correlates with income and age
income_spend_map = {"<15K": (200, 600), "15K-25K": (400, 1000), 
                    "25K-50K": (700, 1800), "50K-75K": (1200, 3000), ">75K": (2000, 5000)}
df["current_skincare_spend_monthly"] = df["income_bracket"].apply(
    lambda x: int(np.random.normal(
        np.mean(income_spend_map[x]), 
        (income_spend_map[x][1] - income_spend_map[x][0]) / 4
    ))
).clip(lower=100)

# Channel preference — younger and higher income prefer online
online_prob = np.where(df["age"] < 25, 0.55, np.where(df["age"] < 30, 0.45, 0.35))
online_prob = np.where(df["income_bracket"].isin(["50K-75K", ">75K"]), online_prob + 0.15, online_prob)
channel_rand = np.random.random(N)
df["preferred_channel"] = np.where(
    channel_rand < online_prob, "Online",
    np.where(channel_rand < online_prob + 0.25, "Offline", "Both")
)

# Product categories of interest (1-4 categories each)
df["product_categories_interest"] = df.apply(
    lambda row: ", ".join(np.random.choice(
        product_categories, 
        size=np.random.randint(1, 5),
        replace=False,
        p=None  # Uniform selection from categories
    )), axis=1
)

# Brand loyalty score (1-10) — higher in older demographics
df["brand_loyalty_score"] = np.where(
    df["age"] >= 30, 
    np.random.normal(7.0, 1.2, N).clip(1, 10).astype(int),
    np.where(df["age"] >= 25, 
             np.random.normal(5.5, 1.5, N).clip(1, 10).astype(int),
             np.random.normal(4.2, 1.6, N).clip(1, 10).astype(int))
)

# Price sensitivity (1-10) — HIGHER (more sensitive) in Tier-2, lower income
base_price_sens = np.where(
    df["income_bracket"].isin(["<15K", "15K-25K"]), 7.5,
    np.where(df["income_bracket"] == "25K-50K", 6.0, 4.5)
)
df["price_sensitivity"] = np.random.normal(base_price_sens, 1.2, N).clip(1, 10).round(1)

# Natural preference (1-10) — HIGHER in Tier-2 (clean beauty trend)
base_natural = np.where(
    df["city"].isin(["Indore", "Bhopal", "Jaipur"]), 7.2,  # Strong Ayurvedic culture
    6.5
)
df["natural_preference"] = np.random.normal(base_natural, 1.3, N).clip(1, 10).round(1)

# Purchase frequency (times per month)
df["purchase_frequency"] = np.where(
    df["income_bracket"].isin(["50K-75K", ">75K"]),
    np.random.choice([1, 2, 3, 4], N, p=[0.20, 0.40, 0.30, 0.10]),
    np.random.choice([1, 2, 3], N, p=[0.45, 0.40, 0.15])
)

# Awareness of D2C brands (yes/no) — higher in younger, online users
d2c_awareness_prob = 0.55
d2c_awareness_prob = np.where(df["age"] < 25, d2c_awareness_prob + 0.20, d2c_awareness_prob)
d2c_awareness_prob = np.where(df["age"] < 30, d2c_awareness_prob + 0.10, d2c_awareness_prob)
d2c_awareness_prob = np.where(df["preferred_channel"] == "Online", d2c_awareness_prob + 0.10, d2c_awareness_prob)
df["awareness_of_d2c_brands"] = np.where(
    np.random.random(N) < d2c_awareness_prob.clip(0, 0.95), "Yes", "No"
)

# Willingness to try new brand (1-10) — inversely correlated with brand loyalty
base_willingness = 11 - df["brand_loyalty_score"]
df["willingness_to_try_new_brand"] = np.random.normal(base_willingness, 1.0, N).clip(1, 10).round(1)

# Top skin concerns (1-2 per respondent)
df["top_concerns"] = df.apply(
    lambda row: ", ".join(np.random.choice(
        top_concerns_options, size=np.random.randint(1, 3), replace=False
    )), axis=1
)

# Social media influence (1-10) — higher in younger
df["social_media_influence"] = np.where(
    df["age"] < 25, np.random.normal(7.5, 1.3, N).clip(1, 10).round(1),
    np.where(df["age"] < 30, np.random.normal(6.2, 1.5, N).clip(1, 10).round(1),
             np.random.normal(4.8, 1.7, N).clip(1, 10).round(1))
)

# Satisfaction with current products (1-10) — generally moderate in Tier-2
df["satisfaction_current_products"] = np.random.normal(5.5, 1.4, N).clip(1, 10).round(1)

# Add age group label
df["age_group"] = pd.cut(df["age"], bins=[17, 24, 29, 36], labels=["18-24", "25-29", "30-35"])

# Shuffle to remove ordering artifacts
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
df.to_csv(os.path.join(RAW_DIR, "consumer_survey_data.csv"), index=False)
print(f"\nConsumer Survey Data Generated: {len(df)} responses across {df['city'].nunique()} cities")
print(f"  Columns: {list(df.columns)}")
print(f"  City distribution:\n{df['city'].value_counts().to_string()}")


# =============================================================================
# 3. COMPETITIVE LANDSCAPE DATA
# =============================================================================

competitors = {
    "Brand": ["Mamaearth", "Sugar Cosmetics", "Plum", "Wow Skin Science", 
              "MCaffeine", "Dot & Key", "mCaffeine", "Minimalist"],
    "Year_Founded": [2016, 2012, 2014, 2014, 2016, 2018, 2016, 2020],
    "Hero_Product": ["Face Wash", "Lipstick", "Green Tea Serum", "Hair Oil", 
                     "Coffee Face Scrub", "Watermelon Moisturizer", "Coffee Body Scrub", "Vitamin C Serum"],
    "Price_Range_INR": ["199-599", "149-799", "345-895", "199-699",
                        "249-749", "345-995", "249-699", "299-849"],
    "Pricing_Positioning": ["Mass", "Mass-Premium", "Mid-Premium", "Mass",
                            "Mass-Premium", "Mid-Premium", "Mass-Premium", "Mid-Premium"],
    "Natural_Score": [9, 4, 8, 7, 8, 7, 8, 6],  # 1=chemical, 10=fully natural
    "Primary_Channel": ["Omnichannel", "Omnichannel", "Online-first", "Online-first",
                        "Online-first", "Online-first", "Online-first", "Online-first"],
    "Instagram_Followers_M": [2.8, 4.1, 1.2, 1.5, 1.8, 0.9, 1.8, 1.1],
    "Funding_Raised_Cr": ["2400", "1100", "450", "350", "250", "200", "250", "180"],
    "Target_Demographic": ["Young Mothers", "Gen Z Women", "Millennial Women", "Men & Women",
                           "Gen Z & Millennials", "Gen Z Women", "Gen Z & Millennials", "Millennials"],
    "Tier2_Presence": ["Strong", "Moderate", "Moderate", "Moderate",
                       "Moderate", "Limited", "Moderate", "Limited"],
    "Key_USP": ["Toxin-free, Baby care", "Cruelty-free, Bold colors", "100% Vegan", 
                "No Sulphates/Parabens", "Coffee-based", "Korean skincare",
                "Coffee-based skincare", "Clinical actives"],
}

comp_df = pd.DataFrame(competitors)
comp_df.to_csv(os.path.join(PROCESSED_DIR, "competitive_landscape.csv"), index=False)

# Also save market sizing raw data for visualization
market_sizing_steps = pd.DataFrame({
    "Step": [
        "India Skincare TAM",
        "D2C Beauty Market",
        "D2C Skincare (30% of beauty)",
        "Online Channel (25% of D2C skincare)",
        "Tier-2 Cities (35% of online)",
        "SAM (Top-Down)",
        "SOM Year 1 (5% of SAM)"
    ],
    "Value_INR_Crore": [
        round(india_skincare_tam_inr, 0),
        d2c_beauty_market_cr,
        round(d2c_skincare_market_cr, 0),
        round(online_d2c_skincare_cr, 0),
        round(sam_topdown_cr, 0),
        round(sam_topdown_cr, 0),
        round(som_topdown_cr, 0),
    ],
    "Method": ["Top-Down", "Top-Down", "Top-Down", "Top-Down", "Top-Down", "Top-Down", "Top-Down"]
})
market_sizing_steps.to_csv(os.path.join(PROCESSED_DIR, "market_sizing_steps.csv"), index=False)

print(f"\nCompetitive Landscape: {len(comp_df)} brands profiled")
print(f"\nAll data files saved to {RAW_DIR}/ and {PROCESSED_DIR}/")
print("=" * 60)
print("DATA PREPARATION COMPLETE")
print("=" * 60)