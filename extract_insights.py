import pandas as pd
import numpy as np
from collections import Counter
import re
import json

# Read the data
df = pd.read_csv('bakuguide_restaurants.csv')

insights = {
    'summary': {},
    'cuisine': {},
    'pricing': {},
    'features': {},
    'geographic': {},
    'social_media': {},
    'hours': {}
}

# ============================================================================
# SUMMARY INSIGHTS
# ============================================================================
insights['summary']['total_restaurants'] = len(df)
insights['summary']['data_completeness'] = {
    'essential': round(np.mean([(df['name'].notna() & (df['name'] != '')).sum() / len(df) * 100,
                                 (df['address'].notna() & (df['address'] != '')).sum() / len(df) * 100,
                                 (df['phones'].notna() & (df['phones'] != '')).sum() / len(df) * 100]), 1),
    'business_details': round(np.mean([(df['cuisine'].notna() & (df['cuisine'] != '')).sum() / len(df) * 100,
                                       (df['working_hours'].notna() & (df['working_hours'] != '')).sum() / len(df) * 100,
                                       (df['features'].notna() & (df['features'] != '')).sum() / len(df) * 100]), 1)
}

# ============================================================================
# CUISINE INSIGHTS
# ============================================================================
cuisines = []
for cuisine_str in df['cuisine'].dropna():
    if cuisine_str and cuisine_str.strip():
        cuisines.extend([c.strip() for c in str(cuisine_str).split(';')])

cuisine_counts = Counter(cuisines)
insights['cuisine']['total_unique_cuisines'] = len(cuisine_counts)
insights['cuisine']['top_5'] = {k: int(v) for k, v in cuisine_counts.most_common(5)}
insights['cuisine']['restaurants_with_cuisine'] = int((df['cuisine'].notna() & (df['cuisine'] != '')).sum())
insights['cuisine']['percentage'] = round((insights['cuisine']['restaurants_with_cuisine'] / len(df)) * 100, 1)

# Most diverse (multiple cuisines)
multi_cuisine = df[df['cuisine'].notna() & df['cuisine'].str.contains(';', na=False)]
insights['cuisine']['multi_cuisine_count'] = int(len(multi_cuisine))

# ============================================================================
# PRICING INSIGHTS
# ============================================================================
price_data = []
for price in df['avg_cost_2_people'].dropna():
    if price and str(price).strip():
        numbers = re.findall(r'\d+', str(price))
        if numbers:
            avg_price = np.mean([int(n) for n in numbers])
            price_data.append(avg_price)

if price_data:
    insights['pricing']['average_cost'] = round(np.mean(price_data), 2)
    insights['pricing']['median_cost'] = round(np.median(price_data), 2)
    insights['pricing']['min_cost'] = round(min(price_data), 2)
    insights['pricing']['max_cost'] = round(max(price_data), 2)
    insights['pricing']['restaurants_with_pricing'] = len(price_data)

    # Price categories
    insights['pricing']['categories'] = {
        'budget': len([p for p in price_data if p < 15]),
        'mid_range': len([p for p in price_data if 15 <= p <= 40]),
        'premium': len([p for p in price_data if p > 40])
    }

# ============================================================================
# FEATURES INSIGHTS
# ============================================================================
features = []
for feature_str in df['features'].dropna():
    if feature_str and feature_str.strip():
        features.extend([f.strip() for f in str(feature_str).split(';')])

feature_counts = Counter(features)
insights['features']['total_unique_features'] = len(feature_counts)
insights['features']['top_10'] = {k: int(v) for k, v in feature_counts.most_common(10)}
insights['features']['restaurants_with_features'] = (df['features'].notna() & (df['features'] != '')).sum()

# Most featured restaurants
most_featured = df[df['features'].notna()].copy()
most_featured['feature_count'] = most_featured['features'].str.count(';') + 1
if len(most_featured) > 0:
    insights['features']['max_features'] = int(most_featured['feature_count'].max())
    insights['features']['avg_features'] = round(most_featured['feature_count'].mean(), 1)

# ============================================================================
# GEOGRAPHIC INSIGHTS
# ============================================================================
geo_data = df[['latitude', 'longitude']].dropna()
geo_data['latitude'] = pd.to_numeric(geo_data['latitude'], errors='coerce')
geo_data['longitude'] = pd.to_numeric(geo_data['longitude'], errors='coerce')
geo_data = geo_data.dropna()

insights['geographic']['restaurants_with_gps'] = len(geo_data)
insights['geographic']['percentage'] = round((len(geo_data) / len(df)) * 100, 1)

if len(geo_data) > 0:
    insights['geographic']['coverage'] = {
        'lat_min': round(geo_data['latitude'].min(), 4),
        'lat_max': round(geo_data['latitude'].max(), 4),
        'lon_min': round(geo_data['longitude'].min(), 4),
        'lon_max': round(geo_data['longitude'].max(), 4)
    }

# ============================================================================
# SOCIAL MEDIA INSIGHTS
# ============================================================================
insights['social_media'] = {
    'facebook': {
        'count': (df['facebook'].notna() & (df['facebook'] != '')).sum(),
        'percentage': round(((df['facebook'].notna() & (df['facebook'] != '')).sum() / len(df)) * 100, 1)
    },
    'instagram': {
        'count': (df['instagram'].notna() & (df['instagram'] != '')).sum(),
        'percentage': round(((df['instagram'].notna() & (df['instagram'] != '')).sum() / len(df)) * 100, 1)
    },
    'foursquare': {
        'count': (df['foursquare'].notna() & (df['foursquare'] != '')).sum(),
        'percentage': round(((df['foursquare'].notna() & (df['foursquare'] != '')).sum() / len(df)) * 100, 1)
    }
}

# Restaurants with multiple social media
has_facebook = df['facebook'].notna() & (df['facebook'] != '')
has_instagram = df['instagram'].notna() & (df['instagram'] != '')
has_foursquare = df['foursquare'].notna() & (df['foursquare'] != '')

multi_social = df[has_facebook & has_instagram]
insights['social_media']['multi_platform'] = len(multi_social)

# ============================================================================
# WORKING HOURS INSIGHTS
# ============================================================================
insights['hours']['restaurants_with_hours'] = (df['working_hours'].notna() & (df['working_hours'] != '')).sum()
insights['hours']['percentage'] = round((insights['hours']['restaurants_with_hours'] / len(df)) * 100, 1)

# 24/7 restaurants
twenty_four_seven = df[df['working_hours'].notna() & df['working_hours'].str.contains('24', na=False)]
insights['hours']['24_7_count'] = len(twenty_four_seven)

# ============================================================================
# SAVE INSIGHTS
# ============================================================================
with open('insights.json', 'w', encoding='utf-8') as f:
    json.dump(insights, f, indent=2, ensure_ascii=False)

print("=" * 70)
print("KEY INSIGHTS EXTRACTED")
print("=" * 70)

print(f"\n📊 SUMMARY")
print(f"  • Total Restaurants: {insights['summary']['total_restaurants']}")
print(f"  • Essential Data Completeness: {insights['summary']['data_completeness']['essential']}%")
print(f"  • Business Details Completeness: {insights['summary']['data_completeness']['business_details']}%")

print(f"\n🍽️  CUISINE DIVERSITY")
print(f"  • Unique Cuisine Types: {insights['cuisine']['total_unique_cuisines']}")
print(f"  • Top Cuisine: {list(insights['cuisine']['top_5'].keys())[0]} ({list(insights['cuisine']['top_5'].values())[0]} restaurants)")
print(f"  • Restaurants with Multi-Cuisine: {insights['cuisine']['multi_cuisine_count']}")

if 'average_cost' in insights['pricing']:
    print(f"\n💰 PRICING")
    print(f"  • Average Cost (2 people): {insights['pricing']['average_cost']} Manat")
    print(f"  • Price Range: {insights['pricing']['min_cost']}-{insights['pricing']['max_cost']} Manat")
    print(f"  • Budget Restaurants: {insights['pricing']['categories']['budget']}")
    print(f"  • Mid-Range Restaurants: {insights['pricing']['categories']['mid_range']}")
    print(f"  • Premium Restaurants: {insights['pricing']['categories']['premium']}")

print(f"\n✨ FEATURES & AMENITIES")
print(f"  • Unique Features: {insights['features']['total_unique_features']}")
print(f"  • Most Common: {list(insights['features']['top_10'].keys())[0]} ({list(insights['features']['top_10'].values())[0]} restaurants)")
if 'avg_features' in insights['features']:
    print(f"  • Avg Features per Restaurant: {insights['features']['avg_features']}")

print(f"\n📍 GEOGRAPHIC COVERAGE")
print(f"  • Restaurants with GPS: {insights['geographic']['restaurants_with_gps']} ({insights['geographic']['percentage']}%)")

print(f"\n📱 SOCIAL MEDIA PRESENCE")
print(f"  • Facebook: {insights['social_media']['facebook']['count']} ({insights['social_media']['facebook']['percentage']}%)")
print(f"  • Instagram: {insights['social_media']['instagram']['count']} ({insights['social_media']['instagram']['percentage']}%)")
print(f"  • Foursquare: {insights['social_media']['foursquare']['count']} ({insights['social_media']['foursquare']['percentage']}%)")
print(f"  • Multi-Platform: {insights['social_media']['multi_platform']} restaurants")

print(f"\n⏰ OPERATING HOURS")
print(f"  • 24/7 Restaurants: {insights['hours']['24_7_count']}")
print(f"  • Hours Data Available: {insights['hours']['percentage']}%")

print("\n✓ Insights saved to insights.json")
print("=" * 70)
