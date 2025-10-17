"""
Microburbs Investment Score Analysis
Final version with 12-month window and comprehensive formula

Formula: G(35%) + P(15%) + Y(25%) + A(15%) + L(10%) = Total Score (0-100)

Where:
  G = Price Growth (12-month appreciation)
  P = Affordability (median price relative to market)
  Y = Rental Yield (estimated return on investment)
  A = Accessibility (proximity to major roads)
  L = Market Liquidity (transaction activity trends)
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🏆 MICROBURBS INVESTMENT SCORE ANALYSIS")
print("   12-Month Window | Comprehensive Formula")
print("="*80)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n📂 Step 1: Loading data...")
df_trans = pd.read_parquet('transactions.parquet')
df_gnaf = pd.read_parquet('gnaf_prop.parquet')
gdf_roads = gpd.read_file('roads.gpkg')

df_trans['sale_date'] = pd.to_datetime(df_trans['dat'])
df_trans = df_trans[df_trans['price'].notna() & (df_trans['price'] > 0)].copy()

print(f"✅ Loaded {len(df_trans):,} transactions")
print(f"✅ Loaded {len(df_gnaf):,} properties")
print(f"✅ Loaded {len(gdf_roads):,} roads")

# ============================================================================
# STEP 2: DEFINE TIME WINDOWS (12-MONTH ANALYSIS)
# ============================================================================
print("\n⏰ Step 2: Defining time windows...")
latest_date = df_trans['sale_date'].max()
twelve_months_ago = latest_date - pd.DateOffset(months=12)
twenty_four_months_ago = latest_date - pd.DateOffset(months=24)

recent = df_trans[df_trans['sale_date'] >= twelve_months_ago]
previous = df_trans[(df_trans['sale_date'] >= twenty_four_months_ago) & 
                    (df_trans['sale_date'] < twelve_months_ago)]

print(f"   Recent Period: {twelve_months_ago.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")
print(f"   Recent transactions: {len(recent):,}")
print(f"   Previous transactions: {len(previous):,}")

# ============================================================================
# STEP 3: CALCULATE ROAD PROXIMITY
# ============================================================================
print("\n🛣️  Step 3: Calculating road proximity...")
df_with_coords = df_trans.merge(df_gnaf[['gnaf_pid', 'latitude', 'longitude']], 
                                on='gnaf_pid', how='left')

major_roads = gdf_roads[gdf_roads['fclass'].isin(['motorway', 'primary', 'secondary', 'trunk'])]
print(f"   Major roads identified: {len(major_roads)}")

properties_with_geom = df_with_coords[df_with_coords['latitude'].notna()].copy()
properties_with_geom['geometry'] = properties_with_geom.apply(
    lambda row: Point(row['longitude'], row['latitude']), axis=1
)
gdf_properties = gpd.GeoDataFrame(properties_with_geom, geometry='geometry', crs='EPSG:4326')

if len(major_roads) > 0:
    major_roads = major_roads.to_crs('EPSG:4326')
    
    def min_distance_to_roads(point_geom):
        try:
            distances = major_roads.geometry.distance(point_geom)
            return distances.min() * 111000  # Convert to meters
        except:
            return np.nan
    
    recent_with_coords = gdf_properties[gdf_properties['sale_date'] >= twelve_months_ago]
    recent_with_coords['distance_to_major_road_m'] = recent_with_coords.geometry.apply(min_distance_to_roads)
    
    df_with_coords = df_with_coords.merge(
        recent_with_coords[['gnaf_pid', 'distance_to_major_road_m']], 
        on='gnaf_pid', how='left'
    )
    print("   ✅ Road proximity calculated")

# ============================================================================
# STEP 4: CALCULATE INVESTMENT SCORES
# ============================================================================
print("\n🔢 Step 4: Calculating investment scores...")

def estimate_rental_yield(price):
    """Estimate rental yield based on price (Sydney market benchmarks)"""
    if price < 800000:
        return 5.5
    elif price < 1500000:
        return 4.5
    elif price < 3000000:
        return 3.8
    else:
        return 3.2

def get_investment_signal(score):
    """Map score to investment signal"""
    if score > 75:
        return 'STRONG BUY', '> 75', 'Ideal short- to mid-term buy', '#27ae60'
    elif score >= 60:
        return 'BUY', '60-75', 'Moderate risk, solid entry point', '#f39c12'
    elif score >= 45:
        return 'HOLD/ACCUMULATE', '45-60', 'Hold or long-term accumulation', '#3498db'
    elif score >= 30:
        return 'CAUTION', '30-45', 'Caution advised', '#e67e22'
    else:
        return 'AVOID', '< 30', 'Avoid', '#e74c3c'

results = []

for suburb in df_trans['suburb'].unique():
    suburb_all = df_trans[df_trans['suburb'] == suburb]
    suburb_recent = recent[recent['suburb'] == suburb]
    suburb_previous = previous[previous['suburb'] == suburb]
    suburb_coords = df_with_coords[df_with_coords['suburb'] == suburb]
    
    # Minimum 3 transactions required
    if len(suburb_recent) < 3:
        continue
    
    # Component 1: Price Growth (35%)
    recent_median = suburb_recent['price'].median()
    if len(suburb_previous) >= 3:
        previous_median = suburb_previous['price'].median()
        price_growth = ((recent_median - previous_median) / previous_median) * 100
        price_growth_score = min(35, max(0, (price_growth / 10) * 35))
    else:
        price_growth = 0
        price_growth_score = 17.5
    
    # Component 2: Affordability (15%)
    max_price = df_trans['price'].quantile(0.95)
    affordability_score = max(0, 15 - (recent_median / max_price) * 15)
    
    # Component 3: Rental Yield (25%)
    estimated_yield = estimate_rental_yield(recent_median)
    annual_rent = recent_median * estimated_yield / 100
    monthly_rent = annual_rent / 12
    yield_score = min(25, (estimated_yield / 6) * 25)
    
    # Component 4: Accessibility (15%)
    suburb_recent_coords = suburb_coords[suburb_coords['sale_date'] >= twelve_months_ago]
    if len(suburb_recent_coords[suburb_recent_coords['distance_to_major_road_m'].notna()]) > 0:
        avg_distance = suburb_recent_coords['distance_to_major_road_m'].median()
        accessibility_score = max(0, 15 - (avg_distance / 5000) * 15)
    else:
        avg_distance = None
        accessibility_score = 7.5
    
    # Component 5: Market Liquidity (10%)
    recent_count = len(suburb_recent)
    previous_count = len(suburb_previous)
    if previous_count > 0:
        activity_change = ((recent_count - previous_count) / previous_count) * 100
        liquidity_score = min(10, max(0, 5 + (activity_change / 100) * 5))
    else:
        activity_change = 100
        liquidity_score = 8
    
    # Total Score
    total_score = (price_growth_score + affordability_score + 
                   yield_score + accessibility_score + liquidity_score)
    
    # Get investment signal
    action, score_range, signal, color = get_investment_signal(total_score)
    
    results.append({
        'suburb': suburb,
        'total_score': total_score,
        'action': action,
        'score_range': score_range,
        'investment_signal': signal,
        
        # Component scores
        'price_growth_score': price_growth_score,
        'affordability_score': affordability_score,
        'yield_score': yield_score,
        'accessibility_score': accessibility_score,
        'liquidity_score': liquidity_score,
        
        # Raw metrics
        'recent_median_price': recent_median,
        'price_growth_pct': price_growth,
        'estimated_yield_pct': estimated_yield,
        'estimated_monthly_rent': monthly_rent,
        'avg_distance_to_road_m': avg_distance,
        'recent_transactions': recent_count,
        'activity_change_pct': activity_change
    })

final_df = pd.DataFrame(results).sort_values('total_score', ascending=False)

# ============================================================================
# STEP 5: EXPORT RESULTS
# ============================================================================
print("\n💾 Step 5: Exporting results...")
final_df.to_csv('microburbs_final_scores_with_signals.csv', index=False)
print(f"✅ Saved: microburbs_final_scores_with_signals.csv")

# ============================================================================
# STEP 6: GENERATE VISUALIZATION
# ============================================================================
print("\n🎨 Step 6: Generating visualization...")

# [Visualization code - same as before]
# Modern color palette
colors_palette = {
    'primary': '#1a1a2e',
    'bg': '#f5f6fa',
}

def get_score_color(score):
    if score > 75: return '#27ae60'
    elif score >= 70: return '#2ecc71'
    elif score >= 65: return '#58d68d'
    elif score >= 60: return '#f39c12'
    elif score >= 55: return '#e67e22'
    elif score >= 50: return '#3498db'
    else: return '#95a5a6'

# Create figure
fig = plt.figure(figsize=(24, 16))
fig.patch.set_facecolor(colors_palette['bg'])
gs = GridSpec(5, 4, figure=fig, hspace=0.5, wspace=0.4)

suburbs = final_df['suburb'].values
n = len(suburbs)

# Header with interpretation guide
ax_header = fig.add_subplot(gs[0, :])
ax_header.axis('off')

ax_header.text(0.5, 0.75, 'Microburbs Investment Dashboard', 
              ha='center', fontsize=32, fontweight='bold', 
              color=colors_palette['primary'], transform=ax_header.transAxes)

ax_header.text(0.5, 0.50, f'12-Month Analysis | {len(final_df)} Suburbs | {len(recent)} Transactions', 
              ha='center', fontsize=13, color='gray', transform=ax_header.transAxes)

# Interpretation pills
guide_items = [
    ('>75', 'STRONG BUY', '#27ae60'),
    ('60-75', 'BUY', '#f39c12'),
    ('45-60', 'HOLD', '#3498db'),
    ('30-45', 'CAUTION', '#e67e22'),
    ('<30', 'AVOID', '#e74c3c')
]

x_positions = np.linspace(0.08, 0.82, len(guide_items))
for (score_range, label, color), x in zip(guide_items, x_positions):
    pill = mpatches.FancyBboxPatch((x, 0.08), 0.16, 0.25,
                                   boxstyle="round,pad=0.015",
                                   transform=ax_header.transAxes,
                                   facecolor=color, edgecolor='white',
                                   linewidth=3, alpha=0.95)
    ax_header.add_patch(pill)
    
    ax_header.text(x + 0.08, 0.25, label, ha='center', va='center',
                  fontsize=11, fontweight='bold', color='white', 
                  transform=ax_header.transAxes)
    ax_header.text(x + 0.08, 0.13, score_range, ha='center', va='center',
                  fontsize=9, color='white', transform=ax_header.transAxes)

# Note: Additional charts would go here (pie, radar, scatter, bubble, line, heatmap, bars)
# See the Python script in repository for complete visualization code

plt.tight_layout(rect=[0, 0.02, 1, 0.99])
plt.savefig('microburbs_final_with_interpretation.png', dpi=300, bbox_inches='tight', 
           facecolor=colors_palette['bg'], edgecolor='none')
print("✅ Visualization saved: microburbs_final_with_interpretation.png")
plt.close()

# ============================================================================
# STEP 7: PRINT SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📊 ANALYSIS SUMMARY")
print("="*80)

print(f"\n🏆 TOP 5 SUBURBS:")
for i, (idx, row) in enumerate(final_df.iterrows(), 1):
    print(f"   {i}. {row['suburb']:<20} Score: {row['total_score']:.1f}/100 | {row['action']}")

print(f"\n💡 TOP RECOMMENDATION:")
top = final_df.iloc[0]
print(f"   🏆 {top['suburb']}")
print(f"   • Score: {top['total_score']:.1f}/100")
print(f"   • Action: {top['action']}")
print(f"   • Price: ${top['recent_median_price']:,.0f}")
print(f"   • Growth: {top['price_growth_pct']:+.1f}%")
print(f"   • Yield: {top['estimated_yield_pct']:.1f}% (${top['estimated_monthly_rent']:,.0f}/month)")

print(f"\n📁 Files Generated:")
print(f"   1. microburbs_final_scores_with_signals.csv")
print(f"   2. microburbs_final_with_interpretation.png")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)

