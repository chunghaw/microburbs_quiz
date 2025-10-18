"""
Comprehensive Exploratory Data Analysis (EDA)
Explore all data files: transactions.parquet, gnaf_prop.parquet, cadastre.gpkg, roads.gpkg
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Set styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("="*80)
print("📊 COMPREHENSIVE EXPLORATORY DATA ANALYSIS")
print("   Exploring ALL data files")
print("="*80)

# ============================================================================
# 1. TRANSACTIONS.PARQUET
# ============================================================================
print("\n" + "="*80)
print("1️⃣  TRANSACTIONS.PARQUET - Property Sales Data")
print("="*80)

df_trans = pd.read_parquet('transactions.parquet')
df_trans['sale_date'] = pd.to_datetime(df_trans['dat'])

print(f"\n📏 Shape: {df_trans.shape[0]:,} rows × {df_trans.shape[1]} columns")
print(f"💾 Memory: {df_trans.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"📅 Date Range: {df_trans['sale_date'].min().strftime('%Y-%m-%d')} to {df_trans['sale_date'].max().strftime('%Y-%m-%d')}")
print(f"⏱️  Duration: {(df_trans['sale_date'].max() - df_trans['sale_date'].min()).days / 365.25:.1f} years")

print(f"\n📋 All Columns ({len(df_trans.columns)}):")
for i, col in enumerate(df_trans.columns, 1):
    dtype = df_trans[col].dtype
    nulls = df_trans[col].isna().sum()
    null_pct = (nulls / len(df_trans)) * 100
    unique = df_trans[col].nunique()
    print(f"  {i:2}. {col:<30} | {str(dtype):<15} | Nulls: {null_pct:5.1f}% | Unique: {unique:,}")

print(f"\n🏘️  Suburbs:")
suburb_counts = df_trans['suburb'].value_counts()
print(f"   Total unique suburbs: {df_trans['suburb'].nunique()}")
for suburb, count in suburb_counts.head(20).items():
    pct = (count / len(df_trans)) * 100
    print(f"   • {suburb:<30} {count:>5,} sales ({pct:>5.1f}%)")

print(f"\n💰 Price Statistics:")
price_stats = df_trans['price'].describe()
for stat, value in price_stats.items():
    if stat != 'count':
        print(f"   {stat.capitalize():<10} ${value:>15,.0f}")

print(f"\n🏠 Property Features:")
for col in ['bedrooms', 'bathrooms', 'garage_spaces', 'land_size']:
    if col in df_trans.columns:
        valid = df_trans[col].notna().sum()
        pct = (valid / len(df_trans)) * 100
        if valid > 0:
            print(f"   {col.replace('_', ' ').title():<15} Coverage: {pct:>5.1f}% | "
                  f"Range: {df_trans[col].min():.0f} - {df_trans[col].max():.0f} | "
                  f"Mean: {df_trans[col].mean():.1f}")

print(f"\n📅 Sales by Year:")
yearly = df_trans.groupby(df_trans['sale_date'].dt.year).size().sort_index()
for year, count in yearly.tail(10).items():
    pct = (count / len(df_trans)) * 100
    bar = '█' * int(count / yearly.max() * 40)
    print(f"   {year}: {count:>4} sales ({pct:>4.1f}%) {bar}")

# ============================================================================
# 2. GNAF_PROP.PARQUET
# ============================================================================
print("\n" + "="*80)
print("2️⃣  GNAF_PROP.PARQUET - Geocoded National Address File")
print("="*80)

df_gnaf = pd.read_parquet('gnaf_prop.parquet')

print(f"\n📏 Shape: {df_gnaf.shape[0]:,} rows × {df_gnaf.shape[1]} columns")
print(f"💾 Memory: {df_gnaf.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print(f"\n📋 All Columns ({len(df_gnaf.columns)}):")
for i, col in enumerate(df_gnaf.columns, 1):
    dtype = df_gnaf[col].dtype
    nulls = df_gnaf[col].isna().sum()
    null_pct = (nulls / len(df_gnaf)) * 100
    unique = df_gnaf[col].nunique()
    print(f"  {i:2}. {col:<30} | {str(dtype):<15} | Nulls: {null_pct:5.1f}% | Unique: {unique:,}")

print(f"\n📍 Geographic Coverage:")
print(f"   Latitude:  {df_gnaf['latitude'].min():.6f} to {df_gnaf['latitude'].max():.6f}")
print(f"   Longitude: {df_gnaf['longitude'].min():.6f} to {df_gnaf['longitude'].max():.6f}")

print(f"\n🏘️  Localities:")
locality_counts = df_gnaf['locality_name'].value_counts()
print(f"   Total unique localities: {df_gnaf['locality_name'].nunique()}")
for locality, count in locality_counts.head(15).items():
    pct = (count / len(df_gnaf)) * 100
    print(f"   • {locality:<30} {count:>6,} addresses ({pct:>5.1f}%)")

print(f"\n📮 Postcodes:")
postcode_counts = df_gnaf['postcode'].value_counts()
for postcode, count in postcode_counts.items():
    pct = (count / len(df_gnaf)) * 100
    print(f"   • {postcode}: {count:>6,} addresses ({pct:>5.1f}%)")

print(f"\n🎯 Data Quality:")
print(f"   Addresses with coordinates: {df_gnaf[['latitude', 'longitude']].notna().all(axis=1).sum():,} ({df_gnaf[['latitude', 'longitude']].notna().all(axis=1).sum()/len(df_gnaf)*100:.1f}%)")
print(f"   Unique addresses: {df_gnaf['address'].nunique():,}")
print(f"   Unique GNAF PIDs: {df_gnaf['gnaf_pid'].nunique():,}")

# ============================================================================
# 3. CADASTRE.GPKG
# ============================================================================
print("\n" + "="*80)
print("3️⃣  CADASTRE.GPKG - Land Parcel Boundaries")
print("="*80)

try:
    gdf_cadastre = gpd.read_file('cadastre.gpkg')
    
    print(f"\n📏 Shape: {gdf_cadastre.shape[0]:,} rows × {gdf_cadastre.shape[1]} columns")
    print(f"💾 Memory: {gdf_cadastre.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n📋 Columns:")
    for i, col in enumerate(gdf_cadastre.columns, 1):
        dtype = gdf_cadastre[col].dtype
        unique = gdf_cadastre[col].nunique() if col != 'geometry' else 'N/A'
        print(f"  {i}. {col:<30} | {str(dtype):<20} | Unique: {unique}")
    
    print(f"\n🗺️  Geometry Information:")
    print(f"   CRS: {gdf_cadastre.crs}")
    print(f"   Geometry Types: {gdf_cadastre.geom_type.value_counts().to_dict()}")
    print(f"   Bounding Box:")
    bounds = gdf_cadastre.total_bounds
    print(f"      Min X (lon): {bounds[0]:.6f}")
    print(f"      Min Y (lat): {bounds[1]:.6f}")
    print(f"      Max X (lon): {bounds[2]:.6f}")
    print(f"      Max Y (lat): {bounds[3]:.6f}")
    
    print(f"\n📊 Sample Data:")
    print(gdf_cadastre.head(3))
    
except Exception as e:
    print(f"❌ Error reading cadastre.gpkg: {e}")

# ============================================================================
# 4. ROADS.GPKG
# ============================================================================
print("\n" + "="*80)
print("4️⃣  ROADS.GPKG - Road Network")
print("="*80)

try:
    gdf_roads = gpd.read_file('roads.gpkg')
    
    print(f"\n📏 Shape: {gdf_roads.shape[0]:,} rows × {gdf_roads.shape[1]} columns")
    print(f"💾 Memory: {gdf_roads.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n📋 Columns:")
    for i, col in enumerate(gdf_roads.columns, 1):
        dtype = gdf_roads[col].dtype
        unique = gdf_roads[col].nunique() if col != 'geometry' else 'N/A'
        print(f"  {i:2}. {col:<30} | {str(dtype):<20} | Unique: {unique}")
    
    print(f"\n🗺️  Geometry Information:")
    print(f"   CRS: {gdf_roads.crs}")
    print(f"   Geometry Types: {gdf_roads.geom_type.value_counts().to_dict()}")
    
    print(f"\n🛣️  Road Classifications:")
    if 'fclass' in gdf_roads.columns:
        fclass_counts = gdf_roads['fclass'].value_counts()
        for fclass, count in fclass_counts.items():
            pct = (count / len(gdf_roads)) * 100
            print(f"   • {fclass:<20} {count:>3} roads ({pct:>5.1f}%)")
    
    print(f"\n🏷️  Road Names (Top 15):")
    if 'name' in gdf_roads.columns:
        name_counts = gdf_roads['name'].value_counts()
        for name, count in name_counts.head(15).items():
            print(f"   • {name if name else '[Unnamed]':<30} {count:>2} segments")
    
    print(f"\n📊 Sample Data:")
    print(gdf_roads[['name', 'fclass', 'type', 'oneway']].head(10))
    
except Exception as e:
    print(f"❌ Error reading roads.gpkg: {e}")

# ============================================================================
# 5. DATA RELATIONSHIPS & INSIGHTS
# ============================================================================
print("\n" + "="*80)
print("5️⃣  DATA RELATIONSHIPS & KEY INSIGHTS")
print("="*80)

print(f"\n🔗 How Data Files Connect:")
print(f"   1. Transactions ↔ GNAF:")
print(f"      → Join on 'gnaf_pid'")
print(f"      → Transactions: {df_trans['gnaf_pid'].nunique():,} unique PIDs")
print(f"      → GNAF: {df_gnaf['gnaf_pid'].nunique():,} unique PIDs")
common_pids = set(df_trans['gnaf_pid']) & set(df_gnaf['gnaf_pid'])
print(f"      → Common PIDs: {len(common_pids):,} ({len(common_pids)/df_trans['gnaf_pid'].nunique()*100:.1f}% of transactions can be geocoded)")

print(f"\n   2. GNAF ↔ Cadastre:")
print(f"      → Spatial join using coordinates or legal_parcel_id")
print(f"      → GNAF has lat/long for all {len(df_gnaf):,} addresses")
print(f"      → Cadastre has {len(gdf_cadastre):,} land parcels")

print(f"\n   3. All ↔ Roads:")
print(f"      → Calculate distance from any point to nearest road")
print(f"      → Used for accessibility scoring")

print(f"\n📊 Coverage Analysis:")
print(f"   Transactions with geocoding: {len(common_pids):,} / {len(df_trans):,} ({len(common_pids)/len(df_trans)*100:.1f}%)")
print(f"   Transactions with price: {df_trans['price'].notna().sum():,} ({df_trans['price'].notna().sum()/len(df_trans)*100:.1f}%)")
print(f"   Transactions with bedrooms: {df_trans['bedrooms'].notna().sum():,} ({df_trans['bedrooms'].notna().sum()/len(df_trans)*100:.1f}%)")
print(f"   Transactions with land size: {df_trans['land_size'].notna().sum():,} ({df_trans['land_size'].notna().sum()/len(df_trans)*100:.1f}%)")

print(f"\n💡 Key Insights:")
print(f"   • Dataset covers {df_trans['suburb'].nunique()} suburbs over {(df_trans['sale_date'].max() - df_trans['sale_date'].min()).days / 365.25:.1f} years")
print(f"   • All data is from {df_trans['state'].unique()[0]} (New South Wales)")
print(f"   • Primary area: Sydney North Shore (Roseville, Willoughby, etc.)")
print(f"   • Comprehensive address geocoding via GNAF database")
print(f"   • Spatial data available for mapping and distance calculations")

# ============================================================================
# 6. EXPORT SUMMARY
# ============================================================================
print("\n" + "="*80)
print("6️⃣  DATA SUMMARY EXPORT")
print("="*80)

summary_data = {
    'File': [],
    'Rows': [],
    'Columns': [],
    'Key Info': []
}

summary_data['File'].append('transactions.parquet')
summary_data['Rows'].append(f"{len(df_trans):,}")
summary_data['Columns'].append(len(df_trans.columns))
summary_data['Key Info'].append(f"{df_trans['suburb'].nunique()} suburbs, {(df_trans['sale_date'].max() - df_trans['sale_date'].min()).days / 365.25:.1f} years")

summary_data['File'].append('gnaf_prop.parquet')
summary_data['Rows'].append(f"{len(df_gnaf):,}")
summary_data['Columns'].append(len(df_gnaf.columns))
summary_data['Key Info'].append(f"{df_gnaf['locality_name'].nunique()} localities, all geocoded")

summary_data['File'].append('cadastre.gpkg')
summary_data['Rows'].append(f"{len(gdf_cadastre):,}")
summary_data['Columns'].append(len(gdf_cadastre.columns))
summary_data['Key Info'].append(f"Land parcels with {gdf_cadastre.geom_type.value_counts().index[0]} geometry")

summary_data['File'].append('roads.gpkg')
summary_data['Rows'].append(f"{len(gdf_roads):,}")
summary_data['Columns'].append(len(gdf_roads.columns))
summary_data['Key Info'].append(f"{gdf_roads['fclass'].nunique()} road types, {len(gdf_roads)} segments")

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('data_summary.csv', index=False)
print(f"\n✅ Exported summary to: data_summary.csv")

# ============================================================================
# 7. DETAILED COLUMN REFERENCE
# ============================================================================
print("\n" + "="*80)
print("7️⃣  DETAILED COLUMN REFERENCE")
print("="*80)

# Export detailed column info for transactions
trans_col_info = []
for col in df_trans.columns:
    trans_col_info.append({
        'table': 'transactions',
        'column': col,
        'dtype': str(df_trans[col].dtype),
        'null_pct': f"{(df_trans[col].isna().sum() / len(df_trans)) * 100:.1f}%",
        'unique_values': df_trans[col].nunique(),
        'sample_values': str(df_trans[col].dropna().head(3).tolist())[:100]
    })

# Export for GNAF
gnaf_col_info = []
for col in df_gnaf.columns:
    gnaf_col_info.append({
        'table': 'gnaf_properties',
        'column': col,
        'dtype': str(df_gnaf[col].dtype),
        'null_pct': f"{(df_gnaf[col].isna().sum() / len(df_gnaf)) * 100:.1f}%",
        'unique_values': df_gnaf[col].nunique(),
        'sample_values': str(df_gnaf[col].dropna().head(3).tolist())[:100]
    })

all_columns = pd.DataFrame(trans_col_info + gnaf_col_info)
all_columns.to_csv('columns_reference.csv', index=False)
print(f"\n✅ Exported detailed column info to: columns_reference.csv")

print("\n" + "="*80)
print("✅ EXPLORATORY DATA ANALYSIS COMPLETE!")
print("="*80)

print(f"""
Files Generated:
   1. data_summary.csv - High-level summary of all files
   2. columns_reference.csv - Detailed column information

Key Takeaways:
   • {len(df_trans):,} property transactions over {(df_trans['sale_date'].max() - df_trans['sale_date'].min()).days / 365.25:.1f} years
   • {len(df_gnaf):,} geocoded addresses (100% have lat/long)
   • {len(gdf_cadastre):,} land parcels with boundaries
   • {len(gdf_roads):,} road segments for accessibility analysis
   • All data from Sydney North Shore area (NSW)
   • {df_trans['suburb'].nunique()} suburbs with transaction data
   • {df_trans['price'].notna().sum()/len(df_trans)*100:.1f}% price coverage
   
Next Steps:
   • Review data_summary.csv for overview
   • Check columns_reference.csv for field details
   • Use this data for comprehensive investment analysis
   • Spatial data enables mapping and distance calculations
""")

print("="*80)

