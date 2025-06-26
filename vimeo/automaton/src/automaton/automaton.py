import os
import requests
import re
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv # import load_dotenv

load_dotenv()

try:
    from vimeo import VimeoClient
except ImportError:
    print("The 'vimeo' Python library is not installed")
    print("Please install it using: pip install vimeo")
    print("Exiting script.")
    exit()

VIMEO_ACCESS_TOKEN = os.getenv('VIMEO_ACCESS_TOKEN')
VIMEO_CLIENT_SECRET = os.getenv('VIMEO_CLIENT_SECRET')
VIMEO_CLIENT_ID = os.getenv('VIMEO_CLIENT_ID')
DATE_FORMAT = "%Y-%m-%d"
LOOKBACK_HOURS = 48

# List of folder IDs to EXCLUDE from the scan.
# Videos within these folders will NOT be checked or updated.
# IMPORTANT: Use string format for IDs as they are often treated as strings by APIs.
EXCLUDED_FOLDER_IDS = ['11103430', '8219992', '6002849']

client = VimeoClient(
    token=VIMEO_ACCESS_TOKEN,
    key=VIMEO_CLIENT_ID,
    secret=VIMEO_CLIENT_SECRET
)

def get_authenticated_user_id() -> str | None:
    """
    Fetches the authenticated user's ID from the Vimeo API.
    This is used to confirm authentication and might be needed for certain API calls.
    """
    try:
        response = client.get('/me')
        response.raise_for_status()
        user_data = response.json()
        # The user URI Looks like /users/12345678
        user_uri = user_data.get('uri')
        if user_uri:
            return user_uri.split('/')[-1]
        print("Could not find 'uri' in '/me' response.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching authenticated user ID: {e}")
        print(f"Response content: {e.response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error fetching authenticated user ID: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching authenticated user ID: {e}")
    return None

def get_all_user_videos() -> str | None:
    """
    Fetches all videos from the authenticated user's entire library. Handles pagination.
    Included parent_folder.uri to enable folder exclusion.

    Returns:
        list[dict]: A list of dictionaries, each containing video information.
                    Returns an empty list if an error occurs or no videos are found.
    """
    all_videos = []
    page = 1
    per_page = 100 # Maximum allowed by Vimeo

    print(f"Fetching all videos from your Team Library.")
    while True:
        try:
            # using /me/videos to get all videos for the authenticated user
            # Requesting 'name', 'created_time', 'uri', and 'parent_folder.uri' fields\
            response = client.get(
                '/me/videos',
                params={
                    'page': page,
                    'per_page': per_page,
                    'fields': 'name,created_time,uri,parent_folder.uri' # added parent_folder.uri
                }
            )
            response.raise_for_status()

            data = None
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError as json_e:
                print(f" Error decoding JSON response for videos: {json_e}")
                if response is not None:
                    print(f" Raw response content (first 500 chars): {response.text[:500]}...")
                break # Exit loop if JSON is malformed

            if not data: # Check if data is None or empty dict/list after parsing
                print(" Warning: No data or invalid data received in JSON response for videos.")
                break

            videos_on_page = data.get('data', [])
            if not isinstance(videos_on_page, list):
                print(f" Warning: Expected 'data field to be a list, but got {type(videos_on_page)}. Skipping.")
                break # Break if 'data' field isn't a list of videos

            if not videos_on_page:
                break # No more videos

            all_videos.extend(videos_on_page)

            # Check if there are more pages based on Vimeo's 'next' link
            if data.get('paging', {}).get('next') is None: 
                break # No 'next' page link, so this is the last page

            page += 1
            print(f" Fetched page {page-1}, total videos so far: {len(all_videos)}")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error fetching videos: {e}")
            if e.response is not None:
                print(f"Response content: {e.response.text}")
            break
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error fetching videos: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occured while fetching videos: {e}")
            break
    print(f"Finished fetching videos. Total videos found in Team Library: {len(all_videos)}")
    return all_videos

# def get_user_folders(user_id: str) -> list[dict]:
#     """
#     Fetches all folders for a given user from the Vimeo API. Handles pagination.

#     Args:
#         user_id (str): The ID of the Vimeo user.

#     Returns:
#         list[dict]: A list of dictionaries, each containing folder information.
#                     Returns an empty list if an error occurs or no folders are found.
#     """
#     all_folders = []
#     page = 1
#     per_page = 100 # max allowed by Vimeo
    
#     print(f"Fetching folders for User ID: {user_id}")
#     while True:
#         try:
#             response = client.get(
#                 f'/users/{user_id}/folders',
#                 params={'page': page, 'per_page': per_page, 'fields': 'uri,name'} # Request URI and name
#             )
#             response.raise_for_status()

#             data = None
#             try:
#                 data = response.json()
#             except requests.exceptions.JSONDecodeError as json_e:
#                 print(f" Error decoding JSON response for folders: {json_e}")
#                 print(f" Raw response content (first 500 chars): {response.text[:500]}...")
#                 break # Exit loop if JSON is malformed

#             if not data: # Check if data is None or empty dict/list after parsing
#                 print(" Warning: No data or invalid data received in JSON response for folders.")
#                 break

#             folders_on_page = data.get('data', [])

#             if not folders_on_page:
#                 break # No more folders

#             all_folders.extend(folders_on_page)

#             if data.get('paging, {}').get('next') is None:
#                 break # No 'next' page link, so this is the last page

#             page += 1
#             print(f" Fetched page {page-1}, total folders so far: {len(all_folders)}")
        
#         except requests.exceptions.HTTPError as e:
#             print(f"HTTP error fetching folders: {e}")
#             print(f"Response content: {e.response.text}")
#             break
#         except requests.exceptions.ConnectionError as e:
#             print("Connection error fetching folders: {e}")
#             break
#         except Exception as e:
#             print(f"An unexpected error occurred while fetching folders: {e}")
#             break
#     print(f"Finished fetching folders. Total folders found: {len(all_folders)}")
#     return all_folders

# def get_folder_videos(user_id: str, folder_id: str) -> list[dict]:
#     """
#     Fetches all videos within a specific Vimeo album. Handles pagination.

#     Args:
#         user_id (str): The ID of the Vimeo user who owns the folder.
#         folder_id (str): The ID of the Vimeo folder.
#     Returns:
#         list[dict]: A list of dictionaries, each containing video information.
#                     Returns an empty list if an error occurs or no videos are found.
#     """
#     all_videos = []
#     page = 1
#     per_page = 100

#     print(f"Fetching videos from Vimeo Folder ID: {folder_id} for User ID: {user_id}")
#     while True:
#         try:
#             response = client.get(
#                 f'/users/{user_id}/folders/{folder_id}/videos',
#                 params={'page': page, 'per_page': per_page, 'fields': 'name,created_time,uri'}
#             )
#             response.raise_for_status() # Raise an HTTP error for bad responses
#             data= response.json()
#             videos_on_page = data.get('data', [])

#             if not videos_on_page:
#                 break # no more videos

#             all_videos.extend(videos_on_page)

#             # check for more pages
#             if data.get('paging', {}).get('next') is None:
#                 break # last page or fewer than per_page items

#             page += 1
#             print(f"Fetched page {page-1}, total videos so far: {len(all_videos)}")
        
#         except requests.exceptions.HTTPError as e:
#             print(f"HTTP error fetching videos from folder {folder_id}: {e}")
#             print(f"Response content: {e.response.text}")
#             break
#         except requests.exceptions.HTTPError as e:
#             print(f"Connection error fetching videos from folder {folder_id}: {e}")
#             break
#         except Exception as e:
#             print(f"An unexpected error occurred while fetching videos from folder {folder_id}: {e}")
#             break
#     return all_videos # Do not print final total here, it's done in main for cumulative count

def get_video_id_from_uri(uri: str) -> str | None:
    """
    Extracts the Vimeo video ID from its URI (e.g., "/videos/123456789").
    """
    if not isinstance(uri, str) or not uri: # Explicit check if it's a non-empty string
        return None
    match = re.search(r'/videos/(\d+)', uri)
    if match:
        return match.group(1)
    return None

def update_video_title(video_id: str, new_title: str) -> bool:
    """
    Updates the title of a specific video on Vimeo.
    """
    response = None
    payload = {
        'name': new_title # the 'name' field is used for the video title
    }
    try:
        # The PATCH method is used to update specific fields of a resource
        response = client.patch(f'/videos/{video_id}', data=payload)
        response.raise_for_status() # raise an HTTP error for bad response
        print(f" Successfully updated video ID {video_id} title to: '{new_title}'")
        return True
    except requests.exceptions.HTTPError as e:
        print(f" HTTP error updating video title for ID {video_id}: {e}")
        if e.response is not None:
            print(f" Response content: {e.response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f" Connection error updating video title for ID {video_id}: {e}")
    except Exception as e:
        print(f" An unexpected error occurred while updating video title for {video_id}: {e}")
    return False

def main():
    """
    Main function to orchestrate scanning Vimeo Team Library (excluding specified folders)
    for recent videos, and updating their titles.
    """
    if not VIMEO_ACCESS_TOKEN and not (VIMEO_CLIENT_ID and VIMEO_CLIENT_SECRET):
        print("ERROR: Authentication credentials not found.")
        print("Please ensure either VIMEO_ACCESS_TOKEN or both VIMEO_CLIENT_ID and VIMEO_CLIENT_SECRET are set in your .env file.")
        return

    authenticated_user_id = get_authenticated_user_id()
    if not authenticated_user_id:
        print("ERROR: Could not retrieve authenticated user ID. Please check your access token and its scopes.")
        return

    print(f"Authenticated User ID: {authenticated_user_id}")
    print(f"Starting Vimeo Team Library processing (excluding folders: {', '.join(EXCLUDED_FOLDER_IDS)}.)")

    # Calculate the datetime for lookback period
    forty_eight_hours_ago = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\nLooking for videos uploaded in the last {LOOKBACK_HOURS} hours (since {forty_eight_hours_ago.isoformat()}).")

    # fetch all videos from the user's library with parent folder info
    all_user_videos = get_all_user_videos() or []

    if not all_user_videos:
        print("No videos found in your Team Library, or an error occured. Exiting.")
        return

    videos_to_process = []
    skipped_by_folder_count = 0
    skipped_by_time_count = 0

    print(f"\nFiltering videos based on upload time and excluded folders:")
    for i, video_info in enumerate(all_user_videos):
        video_uri = video.info.get('uri')
        upload_date_str = video_info.get('created_time')
        parent_folder_info = video_info.get('parent_folder') # This is a dict if video is in a folder

        video_id = get_video_id_from_uri(video_uri)
        if not video_id:
            print(f" Warning: Video {i+1} missing URI or could not extract ID. Skipping.")
            continue # Skip if video ID cannot be determined

        # 1. Check if video is in an excluded folder
        is_excluded_folder = False
        if parent_folder_info and isinstance(parent_folder_info, dict):
            parent_folder_uri = parent_folder_info.get('uri')
            folder_id = get_folder_id_from_uri(parent_folder_uri)
            if folder_id and folder_id in EXCLUDED_FOLDER_IDS:
                print(f" Video ID {video_id} is in excluded folder ID {folder_id}. Skipping.")
                is_excluded_folder = True
                skipped_by_folder_count += 1
        # Handle videos not in any folder (parent_folder might be None)
        elif parent_folder_info is None:
            # If a video is not in any folder, it effectively passes the folder exclusion check:
            pass
        else:
            print(f" Warning: Video ID {video_id} has unexpected parent_folder type: {type(parent_folder_info)}. Not excluding folder based on this.")
        
        if is_excluded_folder:
            continue # Skip this video if its folder is excluded

        # 2. Check upload time (only for videos not in excluded folders)
        if upload_date_str:
            try:
                video_created_dt = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
                if video_created_dt.tzinfo is None:
                    video_created_dt = video_created_dt.replace(tzinfo=timezeone.utc)

                if video_created_dt > forty_eight_hours_ago:
                    videos_to_process.append(video_info)
                else:
                    print(f" Video ID {video_id} uploaded too long ago ({formatted_date if 'formatted_date' in locals() else 'N/A'}). Skipping by time.")
                    skipped_by_time_count += 1
            except ValueError as e:
                print(f" Warning: Could not parse created_time '{upload_date_str}' for video ID {video_ID}. Error {e}. Skipping.")
        else:
            print(f" Warning Video ID {video_ID} is missing 'created_time'. Skipping.")
        
    print(f"\nFinished filtering. Total videos selected for processing: {len(videos_to_process)}")
    print(f" Skipped by excluded folder: {skipped_by_folder_count} videos")
    print(f" Skipped by upload time (older than {LOOKBACK_HOURS} hours): {skipped_by_time_count} videos")
    

    # get all folders for the user
    all_user_folders = get_user_folders(authenticated_user_id) or []
    if not all_user_folders:
        print("No folders found for the authenticated user, or an error occurred. Exiting.")
        return

    # Filter excluded folders
    folders_to_scan = []
    print(f"\nFiltering folders:")
    for folder in all_user_folders:
        if not isinstance(folder, dict):
            print(f" Warning: Expected dictionary for folder, but get {type(folder)}: {folder}. Skipping this item.")
            continue

        folder_uri = folder.get('uri')
        folder_id = folder_uri.split('/')[-1] if isinstance(folder_uri, str) and folder_uri else None
        folder_name = folder.get('name', 'Unnamed Folder')

        if folder_id and folder_id in EXCLUDED_FOLDER_IDS:
            print(f" Excluding folder: '{folder_name}' (ID: {folder_id})")
        elif folder_id:
            folders_to_scan.append({'id': folder_id, 'name': folder_name})
            print(f" Including folder: '{folder_name}' (ID: {folder_id})")
        else:
            print(f" Skipping folder with invalid URI/ID: {folder_uri}")

    if not folders_to_scan:
        print("No folders remaining to scan after exclusion. Exiting.")
        return

    # Calculate the datetime for 48 hours ago
    forty_eight_hours_ago = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\nLooking for videos uploaded in the last {LOOKBACK_HOURS} hours (since {forty_eight_hours_ago.isoformat()})")

    all_recent_videos_from_scanned_folders = []
    total_videos_scanned_from_folders = 0

    print("\nCollecting videos from included folders:")
    for folder_info in folders_to_scan:
        folder_id = folder_info['id']
        folder_name = folder_info['name']
        print(f"Processing videos in folder: '{folder_name}' (ID: {folder_id})")
        videos_in_current_folder = get_folder_videos(authenticated_user_id, folder_id) or []
        total_videos_scanned_from_folders += len(videos_in_current_folder)

        # filter videos from this folder for recent uploads
        for video in videos_in_current_folder:
            created_time_str = video.get('created_time')
            if created_time_str:
                try:
                    video_created_dt = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
                    if video_created_dt > forty_eight_hours_ago:
                        all_recent_videos_from_scanned_folders.append(video)
                except ValueError as e:
                    print(f" Warning: Could not parse created_time '{created_time_str}' for video {video.get('uri', 'N/A')} in folder {folder_id}. Error: {e}")
            else:
                print(f" Warning: Video URI {video.get('uri', 'N/A')} in folder {folder_id} is missing 'created_time'.")
    
    print(f"Finished collecting videos. Total videos scanned from included folders: {total_videos_scanned_from_folders}")
    print(f"Total recent videos found in included folders: {len(all_recent_videos_from_scanned_folders)}")

    if not all_recent_videos_from_scanned_folders:
        print(f"\nNo new videos found in the last {LOOKBACK_HOURS} hours in the included folders. Exiting.")
        return
        
    processed_count = 0
    skipped_count = 0
    
    print("\nProcessing recent videos for title updates:")
    for i, video_info in enumerate(all_recent_videos_from_scanned_folders):
        video_uri = video_info.get('uri')
        current_title = video_info.get('name')
        upload_date_str = video_info.get('created_time')

        if not video_uri:
            print(f"\nVideo {i+1}: Missing URI in video info. Skipping.")
            skipped_count += 1
            continue

        video_id = get_video_id_from_uri(video_uri)

        if not video_id:
            print(f"\nVideo {i+1} (URI: {video_uri}): Could not extract video ID from URI. Skipping.")
            skipped_count += 1
            continue

        print(f"\nProcessing Video {i+1} (ID: {video_id}):")
        if not current_title:
            print(f"  Could not retrieve current title for video ID {video_id}. Skipping.")
            skipped_count += 1
            continue

        if not upload_date_str:
            print(f" Could not retrieve upload date for video ID {video_id}. Skipping.")
            skipped_count += 1
            continue
        
        print(f"Current Title: '{current_title}'")
        print(f"Upload Data (raw): {upload_date_str}")

        try: 
            dt_object = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00')) # handle 'Z' for UTC
            formatted_date = dt_object.strftime(DATE_FORMAT)
            print(f" Formatted Date: {formatted_date}")

            # Check if the title already contains the date to avoid duplicates
            if formatted_date in current_title:
                print(f" Video title already contains the date '{formatted_date}'. No update needed.")
                skipped_count += 1
                continue

            new_title = f"{current_title} ({formatted_date})"
            print(f" New Title will be: '{new_title}'")

            if update_video_title(video_id, new_title):
                processed_count += 1
            else:
                skipped_count += 1 # count as skipped if update failed

        except ValueError as e:
            print(f" Error parsing date '{upload_date_str}': {e}. Please check DATE_FORMAT. Skipping.")
            skipped_count += 1
        except Exception as e:
            print(f" An unexpected error occurred during date processing or title update for video ID {video_id}: {e}. Skipping.")
            skipped_count += 1

    print(f"\n--- Processing Summary ---")
    print(f"Videos Processing and Updated: {processed_count}")
    print(f"Videos Skipped (error, already dated, or missing info): {skipped_count}")
    print("---------------------------")

if __name__ == "__main__":
    main()