"""
Market Momentum Score Analysis for Australian Property Investors
This script performs comprehensive analysis on property transaction data
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("="*80)
print("🏘️  MARKET MOMENTUM SCORE ANALYSIS")
print("="*80)

# Load data
print("\n📂 Loading data...")
transactions = pd.read_parquet('transactions.parquet')
gnaf_properties = pd.read_parquet('gnaf_prop.parquet')

print(f"✅ Loaded {len(transactions):,} transactions")
print(f"✅ Loaded {len(gnaf_properties):,} property records")

# Clean and prepare data
df = transactions.copy()
df = df[df['price'].notna() & (df['price'] > 0)].copy()
df = df[df['suburb'].notna()].copy()

df['sale_date'] = pd.to_datetime(df['dat'])
df['year'] = df['sale_date'].dt.year
df['quarter'] = df['sale_date'].dt.to_period('Q')
df['month'] = df['sale_date'].dt.to_period('M')

df['price_per_sqm'] = np.where(
    (df['land_size'].notna()) & (df['land_size'] > 0),
    df['price'] / df['land_size'],
    np.nan
)

print(f"✅ Prepared {len(df):,} valid transactions")
print(f"📅 Date range: {df['sale_date'].min().strftime('%Y-%m-%d')} to {df['sale_date'].max().strftime('%Y-%m-%d')}")

# Calculate momentum scores
def calculate_momentum_score(df):
    """Calculate Market Momentum Score for each suburb"""
    latest_date = df['sale_date'].max()
    six_months_ago = latest_date - pd.DateOffset(months=6)
    twelve_months_ago = latest_date - pd.DateOffset(months=12)
    
    recent = df[df['sale_date'] >= six_months_ago].copy()
    previous = df[(df['sale_date'] >= twelve_months_ago) & (df['sale_date'] < six_months_ago)].copy()
    
    results = []
    
    for suburb in df['suburb'].unique():
        recent_suburb = recent[recent['suburb'] == suburb]
        previous_suburb = previous[previous['suburb'] == suburb]
        
        if len(recent_suburb) < 3:
            continue
            
        # Price Growth Score (40 points)
        recent_median = recent_suburb['price'].median()
        if len(previous_suburb) >= 3:
            previous_median = previous_suburb['price'].median()
            price_growth = ((recent_median - previous_median) / previous_median) * 100
            price_score = min(40, max(0, (price_growth / 10) * 40))
        else:
            price_growth = 0
            price_score = 20
        
        # Market Activity Score (30 points)
        recent_count = len(recent_suburb)
        if len(previous_suburb) > 0:
            activity_change = ((recent_count - len(previous_suburb)) / len(previous_suburb)) * 100
            activity_score = min(30, max(0, 15 + (activity_change / 50) * 15))
        else:
            activity_change = 100
            activity_score = 25
        
        # Value Score (30 points)
        if recent_suburb['price_per_sqm'].notna().sum() >= 3:
            recent_ppsm = recent_suburb['price_per_sqm'].median()
            overall_ppsm = df[df['suburb'] == suburb]['price_per_sqm'].median()
            
            if pd.notna(overall_ppsm) and overall_ppsm > 0:
                value_ratio = recent_ppsm / overall_ppsm
                if 0.95 <= value_ratio <= 1.15:
                    value_score = 30
                elif value_ratio < 0.95:
                    value_score = 20
                else:
                    value_score = 15
            else:
                value_score = 20
        else:
            value_score = 20
        
        momentum_score = price_score + activity_score + value_score
        
        if momentum_score >= 80:
            category = '🔥 Hot Market'
        elif momentum_score >= 60:
            category = '📈 Growing'
        elif momentum_score >= 40:
            category = '⚖️ Stable'
        elif momentum_score >= 20:
            category = '📉 Cooling'
        else:
            category = '❄️ Cold'
        
        results.append({
            'suburb': suburb,
            'momentum_score': round(momentum_score, 1),
            'category': category,
            'recent_median_price': recent_median,
            'price_growth_6m': round(price_growth, 1),
            'recent_transactions': recent_count,
            'activity_change': round(activity_change, 1),
            'price_score': round(price_score, 1),
            'activity_score': round(activity_score, 1),
            'value_score': round(value_score, 1)
        })
    
    return pd.DataFrame(results).sort_values('momentum_score', ascending=False)

print("\n🔢 Calculating momentum scores...")
momentum_df = calculate_momentum_score(df)
print(f"✅ Calculated scores for {len(momentum_df)} suburbs")

# Export results
momentum_df.to_csv('market_momentum_scores.csv', index=False)
print(f"✅ Exported: market_momentum_scores.csv")

top_suburbs = momentum_df.head(10)['suburb'].values
top_suburbs_transactions = df[df['suburb'].isin(top_suburbs)].copy()
top_suburbs_transactions = top_suburbs_transactions.merge(
    momentum_df[['suburb', 'momentum_score', 'category']], on='suburb', how='left'
)
top_suburbs_transactions.to_csv('top_suburbs_transactions.csv', index=False)
print(f"✅ Exported: top_suburbs_transactions.csv")

# Generate visualizations
print("\n🎨 Generating visualizations...")

# Main overview
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

axes[0, 0].hist(momentum_df['momentum_score'], bins=20, color='steelblue', edgecolor='black', alpha=0.7)
axes[0, 0].axvline(momentum_df['momentum_score'].mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {momentum_df["momentum_score"].mean():.1f}')
axes[0, 0].axvline(momentum_df['momentum_score'].median(), color='green', linestyle='--', linewidth=2, 
                   label=f'Median: {momentum_df["momentum_score"].median():.1f}')
axes[0, 0].set_xlabel('Market Momentum Score', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Number of Suburbs', fontsize=12, fontweight='bold')
axes[0, 0].set_title('Distribution of Market Momentum Scores', fontsize=14, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

category_counts = momentum_df['category'].value_counts()
colors = ['#ff4444', '#ff9944', '#ffdd44', '#44ff44', '#4444ff']
axes[0, 1].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
               startangle=90, colors=colors[:len(category_counts)], textprops={'fontsize': 11, 'fontweight': 'bold'})
axes[0, 1].set_title('Market Category Distribution', fontsize=14, fontweight='bold')

scatter = axes[1, 0].scatter(momentum_df['price_growth_6m'], momentum_df['momentum_score'], 
                             c=momentum_df['recent_transactions'], cmap='viridis', 
                             s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
axes[1, 0].set_xlabel('6-Month Price Growth (%)', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Market Momentum Score', fontsize=12, fontweight='bold')
axes[1, 0].set_title('Price Growth vs Momentum Score', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[1, 0])
cbar.set_label('Recent Transactions', fontsize=11, fontweight='bold')

top_15 = momentum_df.head(15).sort_values('momentum_score')
bars = axes[1, 1].barh(range(len(top_15)), top_15['momentum_score'], color='coral', edgecolor='black')
axes[1, 1].set_yticks(range(len(top_15)))
axes[1, 1].set_yticklabels(top_15['suburb'], fontsize=10)
axes[1, 1].set_xlabel('Momentum Score', fontsize=12, fontweight='bold')
axes[1, 1].set_title('Top 15 Suburbs by Momentum Score', fontsize=14, fontweight='bold')
axes[1, 1].grid(axis='x', alpha=0.3)

for i, (idx, row) in enumerate(top_15.iterrows()):
    axes[1, 1].text(row['momentum_score'] + 1, i, f"{row['momentum_score']:.1f}", 
                    va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('market_momentum_overview.png', dpi=300, bbox_inches='tight')
print("✅ Saved: market_momentum_overview.png")
plt.close()

# Category analysis
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

category_order = ['🔥 Hot Market', '📈 Growing', '⚖️ Stable', '📉 Cooling', '❄️ Cold']
available_categories = [cat for cat in category_order if cat in momentum_df['category'].unique()]

sns.boxplot(data=momentum_df, y='category', x='recent_median_price', 
            order=available_categories, palette='Set2', ax=axes[0])
axes[0].set_xlabel('Recent Median Price ($)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Market Category', fontsize=12, fontweight='bold')
axes[0].set_title('Price Distribution by Market Category', fontsize=14, fontweight='bold')
axes[0].grid(axis='x', alpha=0.3)

sns.boxplot(data=momentum_df, y='category', x='recent_transactions', 
            order=available_categories, palette='Set2', ax=axes[1])
axes[1].set_xlabel('Recent Transactions (6 months)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Market Category', fontsize=12, fontweight='bold')
axes[1].set_title('Transaction Volume by Market Category', fontsize=14, fontweight='bold')
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('market_category_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Saved: market_category_analysis.png")
plt.close()

# Print comprehensive summary
print("\n" + "="*80)
print("📊 ANALYSIS SUMMARY & INVESTMENT INSIGHTS")
print("="*80)

print(f"\n🏆 TOP 10 SUBURBS BY MOMENTUM SCORE:")
print(f"{'Rank':<6}{'Suburb':<25}{'Score':<8}{'Category':<18}{'Growth':<10}{'Median Price'}")
print("-" * 80)
for i, (idx, row) in enumerate(momentum_df.head(10).iterrows(), 1):
    print(f"{i:<6}{row['suburb']:<25}{row['momentum_score']:<8.1f}{row['category']:<18}{row['price_growth_6m']:>6.1f}%   ${row['recent_median_price']:>12,.0f}")

print(f"\n📈 MARKET DISTRIBUTION:")
for category in available_categories:
    count = len(momentum_df[momentum_df['category'] == category])
    pct = count / len(momentum_df) * 100
    print(f"   {category}: {count} suburbs ({pct:.1f}%)")

print(f"\n💡 KEY STATISTICS:")
print(f"   Average Momentum Score: {momentum_df['momentum_score'].mean():.1f}")
print(f"   Median Momentum Score: {momentum_df['momentum_score'].median():.1f}")
print(f"   Average Price Growth (6m): {momentum_df['price_growth_6m'].mean():.1f}%")
print(f"   Median Price Growth (6m): {momentum_df['price_growth_6m'].median():.1f}%")
print(f"   Suburbs with Positive Growth: {(momentum_df['price_growth_6m'] > 0).sum()} ({(momentum_df['price_growth_6m'] > 0).sum()/len(momentum_df)*100:.1f}%)")
print(f"   Suburbs with Increasing Activity: {(momentum_df['activity_change'] > 0).sum()} ({(momentum_df['activity_change'] > 0).sum()/len(momentum_df)*100:.1f}%)")

# Investment recommendations
hot_markets = momentum_df[momentum_df['category'] == '🔥 Hot Market']
growing_markets = momentum_df[momentum_df['category'] == '📈 Growing']

print(f"\n🎯 INVESTMENT RECOMMENDATIONS:")

if len(hot_markets) > 0:
    print(f"\n🔥 HOT MARKETS ({len(hot_markets)} suburbs):")
    print("   → Strong buy signals with high momentum")
    print("   → Act quickly as competition is high")
    print("   → Best for short to medium-term gains")
    for idx, row in hot_markets.head(5).iterrows():
        print(f"   • {row['suburb']}: Score {row['momentum_score']:.1f} | Growth: {row['price_growth_6m']:.1f}% | ${row['recent_median_price']:,.0f}")

if len(growing_markets) > 0:
    print(f"\n📈 GROWING MARKETS ({len(growing_markets)} suburbs):")
    print("   → Positive momentum with good potential")
    print("   → Lower competition than hot markets")
    print("   → Recommended for most investors")
    for idx, row in growing_markets.head(5).iterrows():
        print(f"   • {row['suburb']}: Score {row['momentum_score']:.1f} | Growth: {row['price_growth_6m']:.1f}% | ${row['recent_median_price']:,.0f}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print(f"\n📁 Generated Files:")
print("   • market_momentum_scores.csv")
print("   • top_suburbs_transactions.csv")
print("   • market_momentum_overview.png")
print("   • market_category_analysis.png")

if __name__ == "__main__":
    print("\n✨ Run complete. Check the generated files for detailed results.")

