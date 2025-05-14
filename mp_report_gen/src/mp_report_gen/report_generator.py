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
        response.raise_for_status()
        data = response.json()
        all_events.extend(data.get('objects', []))
        url = data.get('NextPageLink') # handle pagination

    return all_events

def generate_report(events):
    """Create a formatted report"""
    # process data
    df = pd.DataFrame(events)

    # basic cleaning/formatting
    if 'Event_Start_Date' in df.columns:
        df['Event_Start_Date'] = pd.to_datetime(df['Event_Start_Date'])

    # Select relevant columns
    report_df = df[[
        'Event_ID',
        'Event_Title',
        'Event_Start_Date',
        'Event_End_Date',
        'Location_Name',
        'Event_Attendance'
    ]].copy()

    # generate Excel report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'event_report_{timestamp}.xlsx'
    report_df.to_excel(filename, index=False)
    return filename

def main():
    try:
        # Authenticate
        token = get_access_token()

        # set query parameters
        params = {
            '$select': 'Event_ID,Event_Title,Event_Start_Date,Event_End_Date,Location_Name,Event_Attendance',
            '$filter': "Event_Start_Date gt '2024-01-01'",
            '$orderby': 'Event_Start_Date desc'
        }

        # get data
        events = get_events(token, params)

        # generate report
        report_file = generate_report(events)
        print(f"Report generated: {report_file}")

    except Exception as e:
        print(f"Error: {str(e)}")

