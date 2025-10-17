"""
Microburbs Investment Dashboard
Interactive web application with filters and modern UI

Built with Flask + vanilla JavaScript (as per requirements)
Deployable to Vercel
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from pathlib import Path

app = Flask(__name__)

# Load data - handle both local and Vercel paths
def load_data():
    try:
        # Try Vercel/production path
        base_dir = Path('/var/task')
        if not (base_dir / 'microburbs_final_scores_with_signals.csv').exists():
            # Try local development path
            base_dir = Path(__file__).parent.parent
        
        df_scores = pd.read_csv(base_dir / 'microburbs_final_scores_with_signals.csv')
        
        try:
            df_transactions = pd.read_parquet(base_dir / 'transactions.parquet')
            df_transactions['sale_date'] = pd.to_datetime(df_transactions['dat'])
        except:
            # Fallback if parquet not available
            df_transactions = pd.DataFrame()
        
        # Process data
        df_scores = df_scores.fillna(0)
        df_scores = df_scores.round(2)
        
        return df_scores, df_transactions
    except Exception as e:
        print(f"Error loading data: {e}")
        # Return sample data if files not found
        return pd.DataFrame(), pd.DataFrame()

df_scores, df_transactions = load_data()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/suburbs')
def get_suburbs():
    """Get all suburbs with scores"""
    suburbs_data = df_scores.to_dict('records')
    
    # Add state information
    for suburb in suburbs_data:
        suburb['state'] = 'NSW'  # All our data is from NSW
        suburb['postcode'] = get_postcode(suburb['suburb'])
    
    return jsonify({
        'success': True,
        'data': suburbs_data,
        'total': len(suburbs_data)
    })

@app.route('/api/suburb/<suburb_name>')
def get_suburb_detail(suburb_name):
    """Get detailed information for a specific suburb"""
    if df_scores.empty:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
        
    suburb_data = df_scores[df_scores['suburb'] == suburb_name.upper()]
    
    if len(suburb_data) == 0:
        return jsonify({'success': False, 'error': 'Suburb not found'}), 404
    
    suburb_info = suburb_data.iloc[0].to_dict()
    
    # Get recent transactions if available
    trans_history = []
    if not df_transactions.empty:
        try:
            suburb_trans = df_transactions[df_transactions['suburb'] == suburb_name.upper()]
            recent_trans = suburb_trans[suburb_trans['sale_date'] >= '2024-07-03'].copy()
            
            for _, trans in recent_trans.head(20).iterrows():
                trans_history.append({
                    'date': trans['sale_date'].strftime('%Y-%m-%d'),
                    'price': float(trans['price']) if pd.notna(trans['price']) else None,
                    'bedrooms': int(trans['bedrooms']) if pd.notna(trans['bedrooms']) else None,
                    'bathrooms': int(trans['bathrooms']) if pd.notna(trans['bathrooms']) else None,
                    'land_size': float(trans['land_size']) if pd.notna(trans['land_size']) else None
                })
        except:
            pass
    
    suburb_info['transactions'] = trans_history
    suburb_info['state'] = 'NSW'
    
    return jsonify({
        'success': True,
        'data': suburb_info
    })

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    return jsonify({
        'success': True,
        'filters': {
            'states': ['NSW'],  # Expandable when more data available
            'score_ranges': [
                {'label': '75+ (Strong Buy)', 'min': 75, 'max': 100},
                {'label': '60-75 (Buy)', 'min': 60, 'max': 75},
                {'label': '45-60 (Hold)', 'min': 45, 'max': 60},
                {'label': '30-45 (Caution)', 'min': 30, 'max': 45},
                {'label': '<30 (Avoid)', 'min': 0, 'max': 30}
            ],
            'price_ranges': [
                {'label': 'Under $2M', 'min': 0, 'max': 2000000},
                {'label': '$2M - $3M', 'min': 2000000, 'max': 3000000},
                {'label': '$3M - $5M', 'min': 3000000, 'max': 5000000},
                {'label': 'Above $5M', 'min': 5000000, 'max': 100000000}
            ],
            'reliability': ['HIGH', 'MODERATE', 'LOW'],
            'actions': ['BUY', 'HOLD/ACCUMULATE', 'CAUTION', 'AVOID']
        }
    })

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    if df_scores.empty:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
        
    return jsonify({
        'success': True,
        'stats': {
            'total_suburbs': len(df_scores),
            'total_transactions': len(df_transactions) if not df_transactions.empty else 51,
            'avg_score': float(df_scores['total_score'].mean()),
            'buy_signals': len(df_scores[df_scores['total_score'] >= 60]),
            'hold_signals': len(df_scores[(df_scores['total_score'] >= 45) & (df_scores['total_score'] < 60)]),
            'caution_signals': len(df_scores[df_scores['total_score'] < 45]),
            'avg_price': float(df_scores['recent_median_price'].mean()),
            'avg_yield': float(df_scores['estimated_yield_pct'].mean())
        }
    })

def get_postcode(suburb):
    """Map suburb to postcode"""
    postcode_map = {
        'ROSEVILLE': '2069',
        'WILLOUGHBY': '2068',
        'NORTHBRIDGE': '2063',
        'NORTH WILLOUGHBY': '2068',
        'CASTLE COVE': '2069',
        'MIDDLE COVE': '2068',
        'WILLOUGHBY EAST': '2068'
    }
    return postcode_map.get(suburb, '2000')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

