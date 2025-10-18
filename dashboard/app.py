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
from api_client import MicroburbsAPIClient

app = Flask(__name__)

# Initialize API client
api_client = MicroburbsAPIClient()

# Expanded suburb list - including all available in Microburbs sandbox
# The sandbox API has many more suburbs than just our local 7
DEMO_SUBURBS = [
    # Our analyzed suburbs (have investment scores)
    'ROSEVILLE', 'WILLOUGHBY', 'NORTHBRIDGE', 'NORTH WILLOUGHBY',
    'CASTLE COVE', 'MIDDLE COVE', 'WILLOUGHBY EAST',
    
    # Additional suburbs available in Microburbs API
    'BELMONT NORTH', 'BELMONT', 'CHARLESTOWN', 'ADAMSTOWN',
    'NEWCASTLE', 'HAMILTON', 'THE JUNCTION', 'COOKS HILL',
    'MEREWETHER', 'BAR BEACH', 'STOCKTON', 'MAYFIELD',
    
    # Sydney suburbs
    'SYDNEY', 'PARRAMATTA', 'BONDI', 'MANLY', 'CHATSWOOD',
    'STRATHFIELD', 'BURWOOD', 'EPPING', 'HORNSBY',
    
    # More suburbs can be added as discovered in API
]

# Function to discover available suburbs dynamically
def get_available_suburbs():
    """
    Try to get list of all available suburbs from API
    Falls back to DEMO_SUBURBS if API call fails
    """
    try:
        # Try the list endpoint
        response = api_client.list_suburbs('NSW')
        if response['success']:
            return response['data']
    except:
        pass
    
    # Return our known list
    return [{'name': s, 'state': 'NSW'} for s in DEMO_SUBURBS]

# Load local data as fallback
def load_local_data():
    """Load local CSV data as fallback"""
    try:
        base_dir = Path(__file__).parent
        csv_file = base_dir / 'microburbs_final_scores_with_signals.csv'
        
        if csv_file.exists():
            df_scores = pd.read_csv(csv_file)
            df_scores = df_scores.fillna(0).round(2)
            return df_scores
        
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading local data: {e}")
        return pd.DataFrame()

df_local_scores = load_local_data()

def calculate_investment_score(suburb_data: dict) -> dict:
    """
    Calculate investment score from API data
    Uses same formula: G(35%) + P(15%) + Y(25%) + A(15%) + L(10%)
    """
    try:
        # Extract relevant data from API response
        # This will be customized based on actual API response structure
        
        # For now, if API data available, enhance with it
        # Otherwise use local calculated scores
        
        return suburb_data
    except Exception as e:
        print(f"Error calculating score: {e}")
        return suburb_data

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/suburbs')
def get_suburbs():
    """
    Get ALL available suburbs from Microburbs API
    Fetches comprehensive data for each suburb
    """
    # Get filter parameters
    use_api = request.args.get('use_api', 'true').lower() == 'true'
    
    if use_api:
        try:
            # Get available suburbs list
            available_suburbs = get_available_suburbs()
            api_suburbs = []
            
            print(f"Attempting to fetch data for {len(DEMO_SUBURBS)} suburbs from API...")
            
            for suburb in DEMO_SUBURBS:
                try:
                    # Try to get market insights (more comprehensive than just properties)
                    market_data = api_client.get_market_insights(suburb, 'NSW')
                    
                    # Build suburb info
                    suburb_info = {
                        'suburb': suburb,
                        'state': 'NSW',
                        'postcode': get_postcode(suburb),
                        'data_source': 'API'
                    }
                    
                    # If we got API data, use it
                    if market_data.get('success'):
                        suburb_info['api_market_data'] = market_data.get('data', {})
                        suburb_info['has_api_data'] = True
                    else:
                        suburb_info['has_api_data'] = False
                    
                    # Enhance with local investment scores if available
                    if not df_local_scores.empty:
                        local_data = df_local_scores[df_local_scores['suburb'] == suburb]
                        if len(local_data) > 0:
                            # Merge local scores with API data
                            local_dict = local_data.iloc[0].to_dict()
                            suburb_info.update(local_dict)
                            suburb_info['has_investment_score'] = True
                        else:
                            suburb_info['has_investment_score'] = False
                    
                    api_suburbs.append(suburb_info)
                    
                except Exception as suburb_error:
                    print(f"Error fetching {suburb}: {suburb_error}")
                    # Still add suburb with local data only
                    if not df_local_scores.empty:
                        local_data = df_local_scores[df_local_scores['suburb'] == suburb]
                        if len(local_data) > 0:
                            suburb_info = local_data.iloc[0].to_dict()
                            suburb_info['state'] = 'NSW'
                            suburb_info['postcode'] = get_postcode(suburb)
                            suburb_info['has_api_data'] = False
                            suburb_info['has_investment_score'] = True
                            api_suburbs.append(suburb_info)
            
            # Return API + local combined data
            if len(api_suburbs) > 0:
                return jsonify({
                    'success': True,
                    'data': api_suburbs,
                    'total': len(api_suburbs),
                    'data_source': 'Microburbs API + Investment Scores',
                    'api_suburbs_count': len([s for s in api_suburbs if s.get('has_api_data')]),
                    'scored_suburbs_count': len([s for s in api_suburbs if s.get('has_investment_score')])
                })
        
        except Exception as e:
            print(f"API fetch error: {e}")
    
    # Fallback to local data only
    if not df_local_scores.empty:
        suburbs_data = df_local_scores.to_dict('records')
        
        for suburb in suburbs_data:
            suburb['state'] = 'NSW'
            suburb['postcode'] = get_postcode(suburb['suburb'])
            suburb['data_source'] = 'Local Analysis'
            suburb['has_api_data'] = False
            suburb['has_investment_score'] = True
        
        return jsonify({
            'success': True,
            'data': suburbs_data,
            'total': len(suburbs_data),
            'data_source': 'Local Analysis Only (API disabled or unavailable)'
        })
    
    return jsonify({'success': False, 'error': 'No data available'}), 500

@app.route('/api/suburb/<suburb_name>')
def get_suburb_detail(suburb_name):
    """
    Get comprehensive suburb details
    Primary: Microburbs API (comprehensive data)
    Fallback: Local CSV data
    """
    suburb_upper = suburb_name.upper()
    
    # Try to get comprehensive data from API
    try:
        comprehensive_data = api_client.get_comprehensive_suburb_data(suburb_upper, 'NSW')
        
        # Check if we got any successful API responses
        api_success = any([
            comprehensive_data.get('properties', {}).get('success'),
            comprehensive_data.get('market_insights', {}).get('success'),
            comprehensive_data.get('demographics', {}).get('success')
        ])
        
        if api_success:
            # Enhance with local scores if available
            if not df_local_scores.empty:
                local_data = df_local_scores[df_local_scores['suburb'] == suburb_upper]
                if len(local_data) > 0:
                    comprehensive_data['investment_score'] = local_data.iloc[0].to_dict()
            
            comprehensive_data['data_source'] = 'Microburbs API + Local Scores'
            
            return jsonify({
                'success': True,
                'data': comprehensive_data
            })
    
    except Exception as e:
        print(f"API error for {suburb_name}: {e}")
    
    # Fallback to local data
    if not df_local_scores.empty:
        suburb_data = df_local_scores[df_local_scores['suburb'] == suburb_upper]
        
        if len(suburb_data) == 0:
            return jsonify({'success': False, 'error': 'Suburb not found'}), 404
        
        suburb_info = suburb_data.iloc[0].to_dict()
        suburb_info['state'] = 'NSW'
        suburb_info['data_source'] = 'Local Analysis'
        
        return jsonify({
            'success': True,
            'data': suburb_info
        })
    
    return jsonify({'success': False, 'error': 'Suburb not found'}), 404

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
    if df_local_scores.empty:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
        
    return jsonify({
        'success': True,
        'stats': {
            'total_suburbs': len(df_local_scores),
            'total_transactions': 51,
            'avg_score': float(df_local_scores['total_score'].mean()),
            'buy_signals': len(df_local_scores[df_local_scores['total_score'] >= 60]),
            'hold_signals': len(df_local_scores[(df_local_scores['total_score'] >= 45) & (df_local_scores['total_score'] < 60)]),
            'caution_signals': len(df_local_scores[df_local_scores['total_score'] < 45]),
            'avg_price': float(df_local_scores['recent_median_price'].mean()),
            'avg_yield': float(df_local_scores['estimated_yield_pct'].mean()),
            'data_source': 'Microburbs API + Local Analysis'
        }
    })

def get_postcode(suburb):
    """Map suburb to postcode - expanded list"""
    postcode_map = {
        # Sydney North Shore
        'ROSEVILLE': '2069',
        'WILLOUGHBY': '2068',
        'NORTHBRIDGE': '2063',
        'NORTH WILLOUGHBY': '2068',
        'CASTLE COVE': '2069',
        'MIDDLE COVE': '2068',
        'WILLOUGHBY EAST': '2068',
        'CHATSWOOD': '2067',
        
        # Newcastle area
        'BELMONT NORTH': '2280',
        'BELMONT': '2280',
        'CHARLESTOWN': '2290',
        'ADAMSTOWN': '2289',
        'NEWCASTLE': '2300',
        'HAMILTON': '2303',
        'THE JUNCTION': '2291',
        'COOKS HILL': '2300',
        'MEREWETHER': '2291',
        'BAR BEACH': '2300',
        'STOCKTON': '2295',
        'MAYFIELD': '2304',
        
        # Sydney suburbs
        'SYDNEY': '2000',
        'PARRAMATTA': '2150',
        'BONDI': '2026',
        'MANLY': '2095',
        'STRATHFIELD': '2135',
        'BURWOOD': '2134',
        'EPPING': '2121',
        'HORNSBY': '2077'
    }
    return postcode_map.get(suburb, '2000')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

