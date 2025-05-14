import requests
import csv
from datetime import datetime

# -- Configuration - Replace with correct details
# Your Ministry Platform base API URL (e.g., "https://mychurch.ministryplatform.com/ministryplatformapi")
BASE_API_URL = "YOUR_BASE_API_URL_HERE"
# The specific API endpoint for events (e.g. "tables/Events")
EVENTS_ENDPOINT = "tables/YOUR_EVENTS_TABLE_HERE"
# Auth: This is dependent on MP requirements
# It might be an API key in headers, OAuth token, or other methods.
# Example for an API Key in headers:
API_KEY = "YOUR_API_KEY_HERE"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",  # Or "Basic YOUR_BASE64_ENCODED_CREDENTIALS" or other
    "Content-Type": "application/json",
}

# --- You might need to adjust query parameters based on API documentation ---
# Example: Select specific columns, filter by date, etc.
# Refer to OData query options: https://www.odata.org/getting-started/basic-tutorial/#queryData
# For instance, to select only Event_Title and Start_Date: "$select=Event_Title,Event_Date"
# To filter for events in the next 30 days: "$filter=Event_Date ge " + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ') + " and Event_Date le " + (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
QUERY_PARAMS = {
    "$select": "Event_Title, Start_Date, Location_Name, Congregation_Name, Program_Name, Primary_Contact_Name", # Customize with fields you need
    "$filter": "Cancelled eq false and End_Date ge " + datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), # Example: Get active, future events
    "$orderby": "Start_Date asc", # Order by start date
    # "$top": "50" # Optionally limit the number of results
}

# Report configuration
REPORT_FILENAME = "ministry_platform_events_report.csv"
REPORT_COLUMNS = ["Event Title", "Start Date", "Location", "Congregation", "Program", "Primary Contact"]

def fetch_events_data():
    """Fetches event data from the Ministry Platform API."""
    full_url = f"{BASE_API_URL}/{EVENTS_ENDPOINT}"
    print(f"Attempting to fetch data from: {full_url}")
    print(f"With query parameters: {QUERY_PARAMS}")
    print(f"Using headers: {HEADERS}")

    try:
        # make GET request to the API
        # Ensure MP uses HTTPS
        response = requests.get(full_url, headers=HEADERS, params=QUERY_PARAMS, timeout=30, verify=True)

        # Raise exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Assuming the API returns JSON data
        # The actual structure of the JSON response might vary.
        # Ministry Platform often wraps results in a "value" array for OData.
        # Or it might be a list of records directly. Inspect your API's actual response.
        data = response.json()
        print("Successfully fetched data.")

        # if data is wrapped (e.g. in a 'value' key for 0Data)
        if isinstance(data, dict) and 'value' in data:
            return data['value']
        return data # if it's a direct list of records
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None
    except ValueError as e: # includes JSONDecodeError
        print(f"Error decoding JSON Response: {e}")
        return None
    
def generate_report(events_data, filename=REPORT_FILENAME):
    """Generates a CSV report from the events data"""
    if not events_data:
        print("No event data to generate report.")
        return
    
    print(f"Generating report: {filename}...")
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # write the header row
            writer.writerow(REPORT_COLUMNS)

            # Write the event data rows
            # This part needs to be carefully mapped to your actual data structure
            # and the fields you selected in QUERY_PARAMS
            for event in events_data:
                row = [
                    event.get("Event_Title", "N/A"),
                    event.get("Start_Date", "N/A"), # Consider formatting this date
                    event.get("Location_Name", "N/A"),
                    event.get("Congregation_Name", "N/A"),
                    event.get("Program_Name", "N/A"),
                    event.get("Primary_Contact_Name", "N/A")  
                ]
                writer.writerow(row)
        print(f"Report '{filename}' generated successfully.")
    except IOError as e:
        print(f"Error writing report to file: {e}")
    except KeyError as e:
        print(f"Error processing event data: Missing key {e}. Check your $select query and data structure.")

if __name__ == "__main__":
    
