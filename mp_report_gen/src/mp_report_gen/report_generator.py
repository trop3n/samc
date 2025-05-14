import requests
import pandas as pd 
from datetime import datetime

# Configuration
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
API_BASE_URL = 'https://your-domain.com/ministryplatformapi/'
EVENTS_ENDPOINT = 'tables/events'

def get_access_token():
    """Authenticate and get OAuth2 access token"""
    auth_url = f"{API_BASE_URL}/oauth/connect/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(auth_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_events(access_token, params=None):
    """Fetch events from API with pagination"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'applications/json'
    }

    all_events = []
    url = f"{API_BASE_URL}/{EVENTS_ENDPOINT}"

    while url:
        response = requests.get(url, headers=headers, params=params)