import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import re

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read data
df = pd.read_csv('bakuguide_restaurants.csv')

print("Generating business intelligence charts...")

import os
os.makedirs('charts', exist_ok=True)

# ============================================================================
# 1. MARKET OPPORTUNITY - Cuisine Gaps Analysis
# ============================================================================
print("\n1. Creating market opportunity analysis...")

cuisines = []
for cuisine_str in df['cuisine'].dropna():
    if cuisine_str and cuisine_str.strip():
        cuisines.extend([c.strip() for c in str(cuisine_str).split(';')])

cuisine_counts = Counter(cuisines)
top_cuisines = dict(cuisine_counts.most_common(10))

fig, ax = plt.subplots(figsize=(14, 8))
colors_gradient = plt.cm.RdYlGn_r(np.linspace(0.3, 0.8, len(top_cuisines)))
bars = ax.barh(list(top_cuisines.keys()), list(top_cuisines.values()), color=colors_gradient, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Number of Restaurants', fontsize=13, fontweight='bold')
ax.set_ylabel('Cuisine Type', fontsize=13, fontweight='bold')
ax.set_title('Baku Restaurant Market: Cuisine Saturation Analysis', fontsize=16, fontweight='bold', pad=20)

# Add market saturation annotations
for i, (bar, (cuisine, count)) in enumerate(zip(bars, top_cuisines.items())):
    width = bar.get_width()

    # Market status
    if count > 80:
        status = "SATURATED"
        color = '#e74c3c'
    elif count > 40:
        status = "COMPETITIVE"
        color = '#f39c12'
    else:
        status = "OPPORTUNITY"
        color = '#2ecc71'

    ax.text(width + 3, bar.get_y() + bar.get_height()/2,
            f'{int(width)} | {status}',
            va='center', fontsize=11, fontweight='bold', color=color)

# Add market share percentages
total_restaurants = len(df)
for i, (cuisine, count) in enumerate(top_cuisines.items()):
    share = (count / total_restaurants) * 100
    ax.text(-5, i, f'{share:.1f}%', va='center', ha='right', fontsize=10, fontweight='bold', color='#34495e')

ax.text(0.02, 0.98, 'Market Share %', transform=ax.transAxes,
        fontsize=10, verticalalignment='top', fontweight='bold', color='#34495e')

plt.tight_layout()
plt.savefig('charts/market_opportunity_cuisine.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 2. PRICE VS VALUE - Premium Features Analysis
# ============================================================================
print("2. Creating price-to-value analysis...")

# Extract pricing and features
price_feature_data = []
for idx, row in df.iterrows():
    if pd.notna(row['avg_cost_2_people']) and row['avg_cost_2_people']:
        numbers = re.findall(r'\d+', str(row['avg_cost_2_people']))
        if numbers:
            avg_price = np.mean([int(n) for n in numbers])

            feature_count = 0
            if pd.notna(row['features']) and row['features']:
                feature_count = len(row['features'].split(';'))

            cuisine_diversity = 0
            if pd.notna(row['cuisine']) and row['cuisine']:
                cuisine_diversity = len(row['cuisine'].split(';'))

            price_feature_data.append({
                'price': avg_price,
                'features': feature_count,
                'cuisine_diversity': cuisine_diversity,
                'name': row['name']
            })

if price_feature_data:
    price_df = pd.DataFrame(price_feature_data)

    fig, ax = plt.subplots(figsize=(14, 9))

    # Create scatter with size based on cuisine diversity
    scatter = ax.scatter(price_df['price'], price_df['features'],
                        s=price_df['cuisine_diversity']*100 + 50,
                        c=price_df['price'], cmap='RdYlGn_r',
                        alpha=0.6, edgecolors='black', linewidth=1)

    # Add trend line
    z = np.polyfit(price_df['price'], price_df['features'], 1)
    p = np.poly1d(z)
    ax.plot(price_df['price'], p(price_df['price']), "r--", linewidth=2, alpha=0.8, label='Value Trend')

    ax.set_xlabel('Average Price for 2 People (Manat)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Features/Amenities', fontsize=13, fontweight='bold')
    ax.set_title('Price vs Value Analysis: Feature Richness by Price Point', fontsize=16, fontweight='bold', pad=20)

    # Add quadrant lines
    median_price = price_df['price'].median()
    median_features = price_df['features'].median()

    ax.axvline(median_price, color='gray', linestyle='--', alpha=0.3, linewidth=2)
    ax.axhline(median_features, color='gray', linestyle='--', alpha=0.3, linewidth=2)

    # Quadrant labels
    ax.text(median_price * 0.5, median_features * 1.8, 'BUDGET\nHIGH VALUE',
            ha='center', fontsize=11, fontweight='bold', color='#2ecc71',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.text(median_price * 1.5, median_features * 1.8, 'PREMIUM\nFULL SERVICE',
            ha='center', fontsize=11, fontweight='bold', color='#e74c3c',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.text(median_price * 0.5, median_features * 0.3, 'BASIC\nECONOMY',
            ha='center', fontsize=11, fontweight='bold', color='#95a5a6',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.text(median_price * 1.5, median_features * 0.3, 'PREMIUM\nLIMITED',
            ha='center', fontsize=11, fontweight='bold', color='#f39c12',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Price Level (Manat)', fontweight='bold')

    # Legend for bubble size
    for cuisine_div in [1, 2, 3]:
        ax.scatter([], [], s=cuisine_div*100 + 50, c='gray', alpha=0.6,
                  label=f'{cuisine_div} Cuisine{"s" if cuisine_div > 1 else ""}')
    ax.legend(title='Cuisine Diversity', loc='upper left', fontsize=9)

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/price_value_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# 3. COMPETITIVE LANDSCAPE - Market Positioning
# ============================================================================
print("3. Creating competitive landscape map...")

fig, ax = plt.subplots(figsize=(14, 8))

# Price categories
price_ranges = {
    'Budget\n(<15 Manat)': (0, 15),
    'Mid-Range\n(15-30 Manat)': (15, 30),
    'Upper Mid\n(30-50 Manat)': (30, 50),
    'Premium\n(50+ Manat)': (50, 200)
}

category_data = []
for category, (min_p, max_p) in price_ranges.items():
    count = len([p for p in price_df['price'] if min_p <= p < max_p])
    avg_features = price_df[(price_df['price'] >= min_p) & (price_df['price'] < max_p)]['features'].mean() if count > 0 else 0
    category_data.append({
        'category': category,
        'count': count,
        'avg_features': avg_features,
        'mid_price': (min_p + max_p) / 2
    })

cat_df = pd.DataFrame(category_data)

# Create grouped bar chart
x = np.arange(len(cat_df))
width = 0.35

bars1 = ax.bar(x - width/2, cat_df['count'], width, label='Number of Restaurants',
               color='#3498db', edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x + width/2, cat_df['avg_features'], width, label='Avg Features',
               color='#e74c3c', edgecolor='black', linewidth=1.5)

ax.set_xlabel('Price Segment', fontsize=13, fontweight='bold')
ax.set_ylabel('Count / Features', fontsize=13, fontweight='bold')
ax.set_title('Competitive Landscape: Restaurant Distribution by Price Segment', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(cat_df['category'], fontsize=11)
ax.legend(fontsize=11, loc='upper left')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add market insights
total_count = cat_df['count'].sum()
for i, row in cat_df.iterrows():
    market_share = (row['count'] / total_count) * 100
    ax.text(i, max(cat_df['count'].max(), cat_df['avg_features'].max()) * 0.9,
            f'{market_share:.1f}%\nmarket',
            ha='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/competitive_landscape.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 4. REVENUE POTENTIAL - Operating Hours Impact
# ============================================================================
print("4. Creating revenue potential analysis...")

hours_categories = {
    '24/7': [],
    'Extended Hours': [],
    'Standard Hours': []
}

for idx, row in df.iterrows():
    if pd.notna(row['working_hours']) and row['working_hours']:
        hours_str = str(row['working_hours']).lower()

        # Get price if available
        price = None
        if pd.notna(row['avg_cost_2_people']) and row['avg_cost_2_people']:
            numbers = re.findall(r'\d+', str(row['avg_cost_2_people']))
            if numbers:
                price = np.mean([int(n) for n in numbers])

        if price:
            if '24' in hours_str or 'saat' in hours_str:
                hours_categories['24/7'].append(price)
            elif any(h in hours_str for h in ['23:', '00:', '01:', '02:']):
                hours_categories['Extended Hours'].append(price)
            else:
                hours_categories['Standard Hours'].append(price)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Chart 1: Average pricing by hours
avg_prices = {k: np.mean(v) if v else 0 for k, v in hours_categories.items()}
colors = ['#e74c3c', '#f39c12', '#3498db']

bars = ax1.bar(avg_prices.keys(), avg_prices.values(), color=colors,
               edgecolor='black', linewidth=1.5)

ax1.set_ylabel('Average Price (Manat)', fontsize=13, fontweight='bold')
ax1.set_title('Revenue Potential: Pricing by Operating Hours', fontsize=14, fontweight='bold', pad=15)

for bar, (cat, price) in zip(bars, avg_prices.items()):
    count = len(hours_categories[cat])
    ax1.text(bar.get_x() + bar.get_width()/2, price + 1,
             f'{price:.1f} M\n({count} restaurants)',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Chart 2: Volume distribution
counts = {k: len(v) for k, v in hours_categories.items()}

wedges, texts, autotexts = ax2.pie(counts.values(), labels=counts.keys(),
                                     autopct='%1.1f%%', colors=colors,
                                     shadow=True, startangle=90)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(12)

for text in texts:
    text.set_fontsize(12)
    text.set_fontweight('bold')

ax2.set_title('Market Distribution by Hours', fontsize=14, fontweight='bold', pad=15)

# Add total count
total = sum(counts.values())
ax2.text(0, -1.3, f'Total: {total} restaurants with pricing data',
         ha='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('charts/revenue_potential_hours.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 5. CUSTOMER ACQUISITION - Digital Presence ROI
# ============================================================================
print("5. Creating digital marketing analysis...")

social_data = []
for idx, row in df.iterrows():
    has_facebook = pd.notna(row['facebook']) and row['facebook'] != ''
    has_instagram = pd.notna(row['instagram']) and row['instagram'] != ''
    has_foursquare = pd.notna(row['foursquare']) and row['foursquare'] != ''

    platform_count = sum([has_facebook, has_instagram, has_foursquare])

    # Get price
    price = None
    if pd.notna(row['avg_cost_2_people']) and row['avg_cost_2_people']:
        numbers = re.findall(r'\d+', str(row['avg_cost_2_people']))
        if numbers:
            price = np.mean([int(n) for n in numbers])

    social_data.append({
        'platforms': platform_count,
        'price': price if price else None,
        'has_any_social': platform_count > 0
    })

social_df = pd.DataFrame(social_data)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Chart 1: Digital presence adoption
platform_counts = social_df['platforms'].value_counts().sort_index()
colors_gradient = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']

bars = ax1.bar(['No Presence', '1 Platform', '2 Platforms', '3+ Platforms'][:len(platform_counts)],
               platform_counts.values,
               color=colors_gradient[:len(platform_counts)],
               edgecolor='black', linewidth=1.5)

ax1.set_ylabel('Number of Restaurants', fontsize=13, fontweight='bold')
ax1.set_title('Digital Marketing Adoption: Social Media Presence', fontsize=14, fontweight='bold', pad=15)

for bar, count in zip(bars, platform_counts.values):
    percentage = (count / len(df)) * 100
    ax1.text(bar.get_x() + bar.get_width()/2, count + 5,
             f'{count}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Chart 2: Social presence vs pricing
social_yes = social_df[social_df['has_any_social'] == True]['price'].dropna()
social_no = social_df[social_df['has_any_social'] == False]['price'].dropna()

avg_social_yes = social_yes.mean() if len(social_yes) > 0 else 0
avg_social_no = social_no.mean() if len(social_no) > 0 else 0

bars2 = ax2.bar(['With Social\nMedia', 'No Social\nMedia'],
                [avg_social_yes, avg_social_no],
                color=['#2ecc71', '#e74c3c'],
                edgecolor='black', linewidth=1.5)

ax2.set_ylabel('Average Price (Manat)', fontsize=13, fontweight='bold')
ax2.set_title('Premium Positioning: Social Media Impact on Pricing', fontsize=14, fontweight='bold', pad=15)

for bar, avg in zip(bars2, [avg_social_yes, avg_social_no]):
    ax2.text(bar.get_x() + bar.get_width()/2, avg + 1,
             f'{avg:.1f} M',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add insight
diff = avg_social_yes - avg_social_no
ax2.text(0.5, 0.95, f'Premium: +{diff:.1f} Manat ({(diff/avg_social_no*100):.1f}% higher)',
         transform=ax2.transAxes, ha='center', va='top',
         fontsize=11, fontweight='bold', color='#2ecc71',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

plt.tight_layout()
plt.savefig('charts/digital_marketing_roi.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 6. AMENITY VALUE - Feature Impact on Pricing
# ============================================================================
print("6. Creating amenity value analysis...")

# Top valuable features
feature_impact = {}
features_list = []

for idx, row in df.iterrows():
    if pd.notna(row['features']) and row['features']:
        features_list.extend([f.strip() for f in row['features'].split(';')])

feature_counts = Counter(features_list)
top_features = dict(feature_counts.most_common(8))

# Calculate average price for restaurants with each feature
for feature in top_features.keys():
    prices_with_feature = []
    for idx, row in df.iterrows():
        if pd.notna(row['features']) and row['features'] and feature in row['features']:
            if pd.notna(row['avg_cost_2_people']) and row['avg_cost_2_people']:
                numbers = re.findall(r'\d+', str(row['avg_cost_2_people']))
                if numbers:
                    prices_with_feature.append(np.mean([int(n) for n in numbers]))

    if prices_with_feature:
        feature_impact[feature] = {
            'avg_price': np.mean(prices_with_feature),
            'count': len(prices_with_feature)
        }

# Sort by average price
sorted_features = sorted(feature_impact.items(), key=lambda x: x[1]['avg_price'], reverse=True)

fig, ax = plt.subplots(figsize=(14, 8))

features_names = [f[0] for f in sorted_features]
features_prices = [f[1]['avg_price'] for f in sorted_features]
features_counts = [f[1]['count'] for f in sorted_features]

# Color by value
colors_impact = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(features_names)))

bars = ax.barh(features_names, features_prices, color=colors_impact,
               edgecolor='black', linewidth=1.5)

ax.set_xlabel('Average Restaurant Price (Manat)', fontsize=13, fontweight='bold')
ax.set_ylabel('Amenity/Feature', fontsize=13, fontweight='bold')
ax.set_title('Amenity Value Analysis: Feature Impact on Restaurant Pricing', fontsize=16, fontweight='bold', pad=20)

# Add price and count labels
for i, (bar, price, count) in enumerate(zip(bars, features_prices, features_counts)):
    ax.text(price + 1, bar.get_y() + bar.get_height()/2,
            f'{price:.1f} M | {count} venues',
            va='center', fontsize=10, fontweight='bold')

# Add median line
median_price = np.median(features_prices)
ax.axvline(median_price, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax.text(median_price, len(features_names) - 0.5, f'  Median: {median_price:.1f}M',
        color='red', fontweight='bold', fontsize=11)

plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/amenity_value_impact.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✓ All business intelligence charts generated!")
print("\nGenerated 6 business-focused charts:")
print("  1. market_opportunity_cuisine.png - Market saturation analysis")
print("  2. price_value_analysis.png - Price vs features quadrant")
print("  3. competitive_landscape.png - Market positioning")
print("  4. revenue_potential_hours.png - Operating hours impact")
print("  5. digital_marketing_roi.png - Social media ROI")
print("  6. amenity_value_impact.png - Feature pricing impact")
