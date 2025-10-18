"""
Microburbs API Client
Handles communication with Microburbs API endpoints
"""

import requests
import os
from typing import Dict, List, Optional

class MicroburbsAPIClient:
    """Client for Microburbs API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://www.microburbs.com.au/report_generator/api"
        self.api_key = api_key or os.getenv('MICROBURBS_API_KEY', 'test')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_properties_for_sale(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get properties currently for sale in a suburb
        Endpoint: /suburb/properties
        """
        try:
            params = {
                'suburb': suburb,
                'state': state
            }
            response = requests.get(
                f"{self.base_url}/suburb/properties",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_market_insights(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get market insights for a suburb
        Endpoint: /suburb/market-insights
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/market-insights",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_demographics(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get demographic information for a suburb
        Endpoint: /suburb/demographics
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/demographics",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_schools(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get schools in a suburb
        Endpoint: /suburb/schools
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/schools",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_amenities(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get amenities in a suburb
        Endpoint: /suburb/amenities
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/amenities",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_suburb_summary(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get comprehensive suburb information
        Endpoint: /suburb/summary
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/summary",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_risk_factors(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get risk factors for a suburb
        Endpoint: /suburb/risk-factors
        """
        try:
            params = {'suburb': suburb, 'state': state}
            response = requests.get(
                f"{self.base_url}/suburb/risk-factors",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_suburbs(self, state: str = 'NSW') -> Dict:
        """
        Get list of available suburbs
        Endpoint: /suburbs/list
        """
        try:
            params = {'state': state}
            response = requests.get(
                f"{self.base_url}/suburbs/list",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_comprehensive_suburb_data(self, suburb: str, state: str = 'NSW') -> Dict:
        """
        Get comprehensive data by combining multiple API calls
        """
        result = {
            'suburb': suburb,
            'state': state,
            'properties': self.get_properties_for_sale(suburb, state),
            'market_insights': self.get_market_insights(suburb, state),
            'demographics': self.get_demographics(suburb, state),
            'schools': self.get_schools(suburb, state),
            'amenities': self.get_amenities(suburb, state),
            'summary': self.get_suburb_summary(suburb, state),
            'risk_factors': self.get_risk_factors(suburb, state)
        }
        
        return result

