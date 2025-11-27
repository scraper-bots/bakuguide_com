import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import re

# Set style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read the data
df = pd.read_csv('bakuguide_restaurants.csv')

print("Generating charts and insights...")
print(f"Total restaurants: {len(df)}")

# Create charts directory if it doesn't exist
import os
os.makedirs('charts', exist_ok=True)

# ============================================================================
# 1. DATA COMPLETENESS CHART
# ============================================================================
print("\n1. Creating data completeness chart...")

completeness_data = {}
for col in df.columns:
    non_empty = (df[col].notna() & (df[col] != '')).sum()
    completeness_data[col] = (non_empty / len(df)) * 100

# Sort by completeness
completeness_sorted = dict(sorted(completeness_data.items(), key=lambda x: x[1], reverse=True))

plt.figure(figsize=(12, 8))
colors = ['#2ecc71' if v >= 70 else '#f39c12' if v >= 40 else '#e74c3c' for v in completeness_sorted.values()]
bars = plt.barh(list(completeness_sorted.keys()), list(completeness_sorted.values()), color=colors)
plt.xlabel('Completeness (%)', fontsize=12, fontweight='bold')
plt.ylabel('Data Field', fontsize=12, fontweight='bold')
plt.title('Data Completeness by Field (491 Restaurants)', fontsize=14, fontweight='bold', pad=20)
plt.xlim(0, 105)

# Add percentage labels
for i, (bar, val) in enumerate(zip(bars, completeness_sorted.values())):
    plt.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
             va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/data_completeness.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 2. CUISINE DISTRIBUTION (TOP 15)
# ============================================================================
print("2. Creating cuisine distribution chart...")

cuisines = []
for cuisine_str in df['cuisine'].dropna():
    if cuisine_str and cuisine_str.strip():
        cuisines.extend([c.strip() for c in str(cuisine_str).split(';')])

cuisine_counts = Counter(cuisines)
top_cuisines = dict(cuisine_counts.most_common(15))

plt.figure(figsize=(12, 8))
colors_gradient = plt.cm.viridis(np.linspace(0.2, 0.9, len(top_cuisines)))
bars = plt.barh(list(top_cuisines.keys()), list(top_cuisines.values()), color=colors_gradient)
plt.xlabel('Number of Restaurants', fontsize=12, fontweight='bold')
plt.ylabel('Cuisine Type', fontsize=12, fontweight='bold')
plt.title('Top 15 Cuisine Types in Baku', fontsize=14, fontweight='bold', pad=20)

# Add count labels
for bar in bars:
    width = bar.get_width()
    plt.text(width + 2, bar.get_y() + bar.get_height()/2, f'{int(width)}',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/cuisine_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 3. PRICE RANGE DISTRIBUTION
# ============================================================================
print("3. Creating price range distribution chart...")

price_data = []
for price in df['avg_cost_2_people'].dropna():
    if price and str(price).strip():
        # Extract numeric values
        numbers = re.findall(r'\d+', str(price))
        if numbers:
            avg_price = np.mean([int(n) for n in numbers])
            price_data.append(avg_price)

if price_data:
    plt.figure(figsize=(12, 7))

    # Create bins
    bins = [0, 10, 20, 30, 40, 50, 100]
    labels = ['<10', '10-20', '20-30', '30-40', '40-50', '50+']

    counts, _, patches = plt.hist(price_data, bins=bins, edgecolor='black', linewidth=1.2)

    # Color the bars
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#9b59b6']
    for patch, color in zip(patches, colors):
        patch.set_facecolor(color)

    plt.xlabel('Average Cost for 2 People (Manat)', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Restaurants', fontsize=12, fontweight='bold')
    plt.title(f'Restaurant Price Range Distribution ({len(price_data)} restaurants with price data)',
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3)

    # Add count labels on bars
    for i, count in enumerate(counts):
        if count > 0:
            plt.text(bins[i] + (bins[i+1] - bins[i])/2, count + 0.5,
                    f'{int(count)}', ha='center', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('charts/price_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# 4. RESTAURANT FEATURES (TOP 15)
# ============================================================================
print("4. Creating restaurant features chart...")

features = []
for feature_str in df['features'].dropna():
    if feature_str and feature_str.strip():
        features.extend([f.strip() for f in str(feature_str).split(';')])

feature_counts = Counter(features)
top_features = dict(feature_counts.most_common(15))

plt.figure(figsize=(12, 8))
colors_gradient = plt.cm.plasma(np.linspace(0.2, 0.9, len(top_features)))
bars = plt.barh(list(top_features.keys()), list(top_features.values()), color=colors_gradient)
plt.xlabel('Number of Restaurants', fontsize=12, fontweight='bold')
plt.ylabel('Feature/Amenity', fontsize=12, fontweight='bold')
plt.title('Top 15 Restaurant Features & Amenities', fontsize=14, fontweight='bold', pad=20)

# Add count labels
for bar in bars:
    width = bar.get_width()
    plt.text(width + 2, bar.get_y() + bar.get_height()/2, f'{int(width)}',
             va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/features_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 5. GEOGRAPHIC DISTRIBUTION (Heatmap)
# ============================================================================
print("5. Creating geographic distribution chart...")

geo_data = df[['latitude', 'longitude']].dropna()
geo_data['latitude'] = pd.to_numeric(geo_data['latitude'], errors='coerce')
geo_data['longitude'] = pd.to_numeric(geo_data['longitude'], errors='coerce')
geo_data = geo_data.dropna()

if len(geo_data) > 0:
    plt.figure(figsize=(14, 10))

    # Create scatter plot with density
    plt.scatter(geo_data['longitude'], geo_data['latitude'],
               alpha=0.6, s=50, c='#e74c3c', edgecolors='black', linewidth=0.5)

    plt.xlabel('Longitude', fontsize=12, fontweight='bold')
    plt.ylabel('Latitude', fontsize=12, fontweight='bold')
    plt.title(f'Geographic Distribution of Restaurants in Baku ({len(geo_data)} locations)',
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('charts/geographic_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# 6. SOCIAL MEDIA PRESENCE
# ============================================================================
print("6. Creating social media presence chart...")

social_media = {
    'Facebook': (df['facebook'].notna() & (df['facebook'] != '')).sum(),
    'Instagram': (df['instagram'].notna() & (df['instagram'] != '')).sum(),
    'Twitter': (df['twitter'].notna() & (df['twitter'] != '')).sum(),
    'Foursquare': (df['foursquare'].notna() & (df['foursquare'] != '')).sum(),
}

plt.figure(figsize=(10, 7))
colors = ['#3b5998', '#E1306C', '#1DA1F2', '#F94877']
bars = plt.bar(social_media.keys(), social_media.values(), color=colors, edgecolor='black', linewidth=1.5)

plt.ylabel('Number of Restaurants', fontsize=12, fontweight='bold')
plt.title('Social Media Presence of Restaurants', fontsize=14, fontweight='bold', pad=20)
plt.ylim(0, max(social_media.values()) * 1.15)

# Add count labels and percentages
for bar, (platform, count) in zip(bars, social_media.items()):
    height = bar.get_height()
    percentage = (count / len(df)) * 100
    plt.text(bar.get_x() + bar.get_width()/2, height + 5,
             f'{int(count)}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/social_media_presence.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 7. WORKING HOURS PATTERN
# ============================================================================
print("7. Creating working hours patterns chart...")

# Analyze working hours
hours_patterns = {
    '24/7': 0,
    'Morning (Before 10am)': 0,
    'Late Night (After 11pm)': 0,
    'Standard (10am-10pm)': 0,
}

for hours in df['working_hours'].dropna():
    hours_str = str(hours).lower()
    if '24' in hours_str or 'saat' in hours_str:
        hours_patterns['24/7'] += 1
    elif any(h in hours_str for h in ['07:00', '08:00', '09:00']):
        hours_patterns['Morning (Before 10am)'] += 1
    elif any(h in hours_str for h in ['23:', '00:', '01:', '02:']):
        hours_patterns['Late Night (After 11pm)'] += 1
    else:
        hours_patterns['Standard (10am-10pm)'] += 1

plt.figure(figsize=(10, 7))
colors = ['#e74c3c', '#f39c12', '#9b59b6', '#3498db']
explode = (0.05, 0, 0, 0)

wedges, texts, autotexts = plt.pie(hours_patterns.values(), labels=hours_patterns.keys(),
                                     autopct='%1.1f%%', colors=colors, explode=explode,
                                     shadow=True, startangle=90)

# Make percentage text bold and larger
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(11)

for text in texts:
    text.set_fontsize(11)
    text.set_fontweight('bold')

plt.title('Restaurant Operating Hours Patterns', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('charts/working_hours_patterns.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# 8. DATA QUALITY OVERVIEW (Dashboard-style)
# ============================================================================
print("8. Creating data quality overview...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('BakuGuide Data Quality Overview', fontsize=16, fontweight='bold', y=0.995)

# Chart 1: Essential vs Optional data
essential = ['name', 'address', 'phones', 'category']
optional = ['cuisine', 'working_hours', 'avg_cost_2_people', 'features']

essential_completeness = np.mean([completeness_data[f] for f in essential])
optional_completeness = np.mean([completeness_data[f] for f in optional])

categories = ['Essential\nData', 'Business\nDetails']
values = [essential_completeness, optional_completeness]
colors_quality = ['#2ecc71', '#f39c12']

bars = ax1.bar(categories, values, color=colors_quality, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Completeness (%)', fontweight='bold')
ax1.set_title('Data Category Completeness', fontweight='bold', pad=10)
ax1.set_ylim(0, 105)

for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 2,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Chart 2: Restaurants with/without images
has_images = (df['images'].notna() & (df['images'] != '')).sum()
no_images = len(df) - has_images

ax2.pie([has_images, no_images], labels=['With Images', 'No Images'],
        autopct='%1.1f%%', colors=['#3498db', '#95a5a6'], startangle=90,
        shadow=True)
ax2.set_title('Image Availability', fontweight='bold', pad=10)

# Chart 3: Restaurants with/without GPS
has_gps = (df['latitude'].notna() & (df['latitude'] != '')).sum()
no_gps = len(df) - has_gps

ax3.pie([has_gps, no_gps], labels=['With GPS', 'No GPS'],
        autopct='%1.1f%%', colors=['#2ecc71', '#95a5a6'], startangle=90,
        shadow=True)
ax3.set_title('GPS Coordinates Availability', fontweight='bold', pad=10)

# Chart 4: Total restaurants by data richness
rich_data = df[(df['cuisine'].notna() & (df['cuisine'] != '')) &
               (df['working_hours'].notna() & (df['working_hours'] != '')) &
               (df['features'].notna() & (df['features'] != ''))].shape[0]

partial_data = df[((df['cuisine'].notna() & (df['cuisine'] != '')) |
                   (df['working_hours'].notna() & (df['working_hours'] != '')) |
                   (df['features'].notna() & (df['features'] != '')))].shape[0] - rich_data

basic_data = len(df) - rich_data - partial_data

ax4.bar(['Rich\nData', 'Partial\nData', 'Basic\nData'],
        [rich_data, partial_data, basic_data],
        color=['#2ecc71', '#f39c12', '#e74c3c'], edgecolor='black', linewidth=1.5)
ax4.set_ylabel('Number of Restaurants', fontweight='bold')
ax4.set_title('Data Richness Distribution', fontweight='bold', pad=10)

for i, (label, val) in enumerate(zip(['Rich\nData', 'Partial\nData', 'Basic\nData'],
                                     [rich_data, partial_data, basic_data])):
    ax4.text(i, val + 5, str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/data_quality_overview.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✓ All charts generated successfully!")
print(f"✓ Charts saved to ./charts/ directory")
print(f"\nGenerated {8} visualization charts:")
print("  1. data_completeness.png")
print("  2. cuisine_distribution.png")
print("  3. price_distribution.png")
print("  4. features_distribution.png")
print("  5. geographic_distribution.png")
print("  6. social_media_presence.png")
print("  7. working_hours_patterns.png")
print("  8. data_quality_overview.png")
