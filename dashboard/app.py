"""
Microburbs Comprehensive Multi-Period Investment Dashboard
Interactive web application with period selection and comprehensive visualizations

Supports: 1-Year, 3-Year, 5-Year, 9-Year analysis periods
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from pathlib import Path

app = Flask(__name__)

# Load all period data
def load_all_period_data():
    """Load all analysis periods"""
    try:
        base_dir = Path(__file__).parent
        
        periods = {}
        for period in ['1_year', '3_year', '5_year', '9_year']:
            csv_file = base_dir / f'investment_scores_{period}.csv'
            if csv_file.exists():
                periods[period] = pd.read_csv(csv_file).fillna(0).round(2)
            else:
                # Try parent directory
                csv_file = base_dir.parent / f'investment_scores_{period}.csv'
                if csv_file.exists():
                    periods[period] = pd.read_csv(csv_file).fillna(0).round(2)
        
        # Load comparison data
        comparison_file = base_dir / 'multi_period_comparison.csv'
        if not comparison_file.exists():
            comparison_file = base_dir.parent / 'multi_period_comparison.csv'
        
        comparison_df = pd.read_csv(comparison_file).fillna(0) if comparison_file.exists() else pd.DataFrame()
        
        return periods, comparison_df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}, pd.DataFrame()

periods_data, comparison_data = load_all_period_data()

# Period display names
PERIOD_NAMES = {
    '1_year': '1-Year',
    '3_year': '3-Year',
    '5_year': '5-Year',
    '9_year': '9-Year'
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/periods')
def get_periods():
    """Get available analysis periods"""
    return jsonify({
        'success': True,
        'periods': [
            {'id': '1_year', 'label': '1-Year (12M Momentum)', 'description': 'Current market conditions'},
            {'id': '3_year', 'label': '3-Year (Post-COVID)', 'description': 'Recovery trends'},
            {'id': '5_year', 'label': '5-Year (Medium-term)', 'description': 'Medium-term performance'},
            {'id': '9_year', 'label': '9-Year (Long-term)', 'description': 'Sustainable growth patterns'}
        ]
    })

@app.route('/api/data/<period_id>')
def get_period_data(period_id):
    """Get data for specific period"""
    if period_id not in periods_data:
        return jsonify({'success': False, 'error': 'Period not found'}), 404
    
    period_df = periods_data[period_id]
    data = period_df.to_dict('records')
    
    return jsonify({
        'success': True,
        'period': PERIOD_NAMES.get(period_id, period_id),
        'data': data,
        'total': len(data)
    })

@app.route('/api/comparison')
def get_comparison():
    """Get multi-period comparison data"""
    if comparison_data.empty:
        return jsonify({'success': False, 'error': 'No comparison data'}), 404
    
    data = comparison_data.to_dict('records')
    
    return jsonify({
        'success': True,
        'data': data,
        'total': len(data)
    })

@app.route('/api/stats/<period_id>')
def get_period_stats(period_id):
    """Get statistics for a specific period"""
    if period_id not in periods_data:
        return jsonify({'success': False, 'error': 'Period not found'}), 404
    
    period_df = periods_data[period_id]
    
    return jsonify({
        'success': True,
        'period': PERIOD_NAMES.get(period_id, period_id),
        'stats': {
            'total_suburbs': len(period_df),
            'avg_score': float(period_df['total_score'].mean()),
            'top_suburb': period_df.iloc[0]['suburb'] if len(period_df) > 0 else None,
            'top_score': float(period_df.iloc[0]['total_score']) if len(period_df) > 0 else 0,
            'avg_growth': float(period_df['price_growth_pct'].mean()),
            'avg_price': float(period_df['period_median_price'].mean()),
            'total_transactions': int(period_df['period_transactions'].sum()),
            'buy_signals': len(period_df[period_df['total_score'] >= 60]),
            'hold_signals': len(period_df[(period_df['total_score'] >= 45) & (period_df['total_score'] < 60)]),
            'caution_signals': len(period_df[period_df['total_score'] < 45])
        }
    })

@app.route('/api/suburb/<suburb_name>')
def get_suburb_across_periods(suburb_name):
    """Get suburb data across all periods"""
    suburb_upper = suburb_name.upper()
    
    result = {
        'suburb': suburb_upper,
        'periods': {}
    }
    
    for period_id, period_df in periods_data.items():
        suburb_data = period_df[period_df['suburb'] == suburb_upper]
        if len(suburb_data) > 0:
            result['periods'][PERIOD_NAMES.get(period_id, period_id)] = suburb_data.iloc[0].to_dict()
    
    if not result['periods']:
        return jsonify({'success': False, 'error': 'Suburb not found'}), 404
    
    return jsonify({
        'success': True,
        'data': result
    })

@app.route('/api/top-performers')
def get_top_performers():
    """Get top 5 performers from each period"""
    result = {}
    
    for period_id, period_df in periods_data.items():
        top_5 = period_df.head(5)
        result[PERIOD_NAMES.get(period_id, period_id)] = top_5.to_dict('records')
    
    return jsonify({
        'success': True,
        'data': result
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
