"""
Comprehensive Multi-Period Investment Analysis
Analyzes 1-year, 3-year, 5-year, and 9-year (2016+) trends

This provides investors with complete picture: short-term momentum + long-term stability
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🏆 COMPREHENSIVE MULTI-PERIOD INVESTMENT ANALYSIS")
print("   1-Year | 3-Year | 5-Year | 9-Year (2016+) Trends")
print("="*80)

# Load data
df_trans = pd.read_parquet('transactions.parquet')
df_gnaf = pd.read_parquet('gnaf_prop.parquet')
gdf_roads = gpd.read_file('roads.gpkg')

df_trans['sale_date'] = pd.to_datetime(df_trans['dat'])
df_trans = df_trans[df_trans['price'].notna() & (df_trans['price'] > 0)].copy()

# Calculate price per sqm
df_trans['price_per_sqm'] = np.where(
    (df_trans['land_size'].notna()) & (df_trans['land_size'] > 0),
    df_trans['price'] / df_trans['land_size'],
    np.nan
)

# Road proximity calculation
df_with_coords = df_trans.merge(df_gnaf[['gnaf_pid', 'latitude', 'longitude']], on='gnaf_pid', how='left')
major_roads = gdf_roads[gdf_roads['fclass'].isin(['motorway', 'primary', 'secondary', 'trunk'])]

if len(major_roads) > 0:
    major_roads = major_roads.to_crs('EPSG:4326')
    properties_with_geom = df_with_coords[df_with_coords['latitude'].notna()].copy()
    properties_with_geom['geometry'] = properties_with_geom.apply(
        lambda row: Point(row['longitude'], row['latitude']), axis=1
    )
    gdf_properties = gpd.GeoDataFrame(properties_with_geom, geometry='geometry', crs='EPSG:4326')
    
    def min_distance_to_roads(point_geom):
        try:
            distances = major_roads.geometry.distance(point_geom)
            return distances.min() * 111000
        except:
            return np.nan
    
    print("Calculating road proximity...")
    # Calculate for properties from 2016+
    from_2016 = gdf_properties[gdf_properties['sale_date'] >= '2016-01-01']
    from_2016['distance_to_major_road_m'] = from_2016.geometry.apply(min_distance_to_roads)
    df_with_coords = df_with_coords.merge(
        from_2016[['gnaf_pid', 'distance_to_major_road_m']], on='gnaf_pid', how='left'
    )

# Define analysis periods
latest_date = df_trans['sale_date'].max()
periods = {
    '1-Year': {'start': latest_date - pd.DateOffset(months=12), 'label': '12M', 'color': '#e74c3c'},
    '3-Year': {'start': latest_date - pd.DateOffset(years=3), 'label': '3Y', 'color': '#f39c12'},
    '5-Year': {'start': latest_date - pd.DateOffset(years=5), 'label': '5Y', 'color': '#3498db'},
    '9-Year': {'start': pd.Timestamp('2016-01-01'), 'label': '9Y', 'color': '#2ecc71'}
}

def estimate_rental_yield(price):
    if price < 800000: return 5.5
    elif price < 1500000: return 4.5
    elif price < 3000000: return 3.8
    else: return 3.2

# Calculate scores for each period
all_results = {}

for period_name, period_info in periods.items():
    print(f"\n{'='*80}")
    print(f"Analyzing {period_name} Period...")
    print(f"{'='*80}")
    
    period_start = period_info['start']
    period_data = df_trans[df_trans['sale_date'] >= period_start]
    
    # For comparison, use equal-length previous period
    period_length = latest_date - period_start
    previous_start = period_start - period_length
    previous_data = df_trans[(df_trans['sale_date'] >= previous_start) & (df_trans['sale_date'] < period_start)]
    
    print(f"   Period: {period_start.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")
    print(f"   Transactions: {len(period_data):,}")
    print(f"   Comparison period: {len(previous_data):,} transactions")
    
    results = []
    
    for suburb in df_trans['suburb'].unique():
        suburb_period = period_data[period_data['suburb'] == suburb]
        suburb_previous = previous_data[previous_data['suburb'] == suburb]
        suburb_coords = df_with_coords[df_with_coords['suburb'] == suburb]
        
        # Skip if no data in period
        if len(suburb_period) == 0:
            continue
        
        # Metrics
        period_count = len(suburb_period)
        period_median = suburb_period['price'].median()
        
        # Price Growth
        if len(suburb_previous) >= 1:
            previous_median = suburb_previous['price'].median()
            price_growth = ((period_median - previous_median) / previous_median) * 100
            price_growth_score = min(35, max(0, (price_growth / 10) * 35))
        else:
            price_growth = 0
            price_growth_score = 17.5
        
        # Affordability
        max_price = df_trans['price'].quantile(0.95)
        affordability_score = max(0, 15 - (period_median / max_price) * 15)
        
        # Rental Yield
        estimated_yield = estimate_rental_yield(period_median)
        yield_score = min(25, (estimated_yield / 6) * 25)
        
        # Accessibility
        period_coords = suburb_coords[suburb_coords['sale_date'] >= period_start]
        if len(period_coords[period_coords['distance_to_major_road_m'].notna()]) > 0:
            avg_distance = period_coords['distance_to_major_road_m'].median()
            accessibility_score = max(0, 15 - (avg_distance / 5000) * 15)
        else:
            avg_distance = None
            accessibility_score = 7.5
        
        # Liquidity
        previous_count = len(suburb_previous)
        if previous_count > 0:
            activity_change = ((period_count - previous_count) / previous_count) * 100
            liquidity_score = min(10, max(0, 5 + (activity_change / 100) * 5))
        else:
            activity_change = 100
            liquidity_score = 8
        
        # Total Score
        total_score = price_growth_score + affordability_score + yield_score + accessibility_score + liquidity_score
        
        # Reliability based on sample size
        if period_count >= 50:
            reliability = 'VERY HIGH'
        elif period_count >= 20:
            reliability = 'HIGH'
        elif period_count >= 10:
            reliability = 'MODERATE'
        elif period_count >= 5:
            reliability = 'LOW'
        else:
            reliability = 'VERY LOW'
        
        results.append({
            'suburb': suburb,
            'period': period_name,
            'total_score': total_score,
            'price_growth_pct': price_growth,
            'period_median_price': period_median,
            'estimated_yield_pct': estimated_yield,
            'estimated_monthly_rent': period_median * estimated_yield / 100 / 12,
            'period_transactions': period_count,
            'activity_change_pct': activity_change,
            'avg_distance_to_road_m': avg_distance,
            'reliability': reliability,
            'price_growth_score': price_growth_score,
            'affordability_score': affordability_score,
            'yield_score': yield_score,
            'accessibility_score': accessibility_score,
            'liquidity_score': liquidity_score
        })
    
    all_results[period_name] = pd.DataFrame(results).sort_values('total_score', ascending=False)
    print(f"   ✅ Analyzed {len(results)} suburbs")

# Export all results
for period_name, df_results in all_results.items():
    filename = f"investment_scores_{period_name.lower().replace('-', '_')}.csv"
    df_results.to_csv(filename, index=False)
    print(f"✅ Exported: {filename}")

# Create comparison dataset
print(f"\n📊 Creating period comparison...")
comparison_data = []

for suburb in df_trans['suburb'].unique():
    suburb_row = {'suburb': suburb}
    
    for period_name in periods.keys():
        period_df = all_results[period_name]
        suburb_data = period_df[period_df['suburb'] == suburb]
        
        if len(suburb_data) > 0:
            row = suburb_data.iloc[0]
            suburb_row[f'{period_name}_score'] = row['total_score']
            suburb_row[f'{period_name}_growth'] = row['price_growth_pct']
            suburb_row[f'{period_name}_price'] = row['period_median_price']
            suburb_row[f'{period_name}_transactions'] = row['period_transactions']
            suburb_row[f'{period_name}_reliability'] = row['reliability']
        else:
            suburb_row[f'{period_name}_score'] = None
            suburb_row[f'{period_name}_growth'] = None
            suburb_row[f'{period_name}_price'] = None
            suburb_row[f'{period_name}_transactions'] = 0
            suburb_row[f'{period_name}_reliability'] = 'NO DATA'
    
    comparison_data.append(suburb_row)

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('multi_period_comparison.csv', index=False)
print(f"✅ Exported: multi_period_comparison.csv")

# Summary report
print(f"\n" + "="*80)
print("📊 MULTI-PERIOD ANALYSIS SUMMARY")
print("="*80)

for period_name, df_results in all_results.items():
    print(f"\n🎯 {period_name} Analysis:")
    print(f"   Suburbs analyzed: {len(df_results)}")
    print(f"   Top 3:")
    for i, (idx, row) in enumerate(df_results.head(3).iterrows(), 1):
        print(f"      {i}. {row['suburb']:<25} Score: {row['total_score']:.1f} | "
              f"Growth: {row['price_growth_pct']:+6.1f}% | "
              f"Reliability: {row['reliability']}")

print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETE!")
print(f"\nGenerated Files:")
print(f"   • investment_scores_1_year.csv")
print(f"   • investment_scores_3_year.csv")
print(f"   • investment_scores_5_year.csv")
print(f"   • investment_scores_9_year.csv")
print(f"   • multi_period_comparison.csv (master comparison)")

ENDOFPYTHON
