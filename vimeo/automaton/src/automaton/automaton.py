import os
import requests
import re
from datetime import datetime
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
VIMEO_FOLDER_ID = os.getenv('VIMEO_FOLDER_ID')
VIMEO_CLIENT_SECRET = os.getenv('VIMEO_CLIENT_SECRET')
VIMEO_CLIENT_ID = os.getenv('VIMEO_CLIENT_ID')
DATE_FORMAT = "%Y-%m-%d"

client = VimeoClient(
    token=VIMEO_ACCESS_TOKEN,
    key=VIMEO_CLIENT_ID,
    secret=VIMEO_CLIENT_SECRET
)

def get_authenticated_user_id() -> str | None:
    """
    Fetches the authenticated user's ID from the Vimeo API.

    Returns:
        str | None: The user ID as a string, or None if an error occurs.
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

def get_folder_videos(user_id: str, folder_id: str) -> list[dict]:
    """
    Fetches all videos within a specific Vimeo album. Handles pagination.

    Args:
        user_id (str): The ID of the Vimeo user who owns the folder.
        folder_id (str): The ID of the Vimeo folder.
    Returns:
        list[dict]: A list of dictionaries, each containing video information.
                    Returns an empty list if an error occurs or no videos are found.
    """
    all_videos = []
    page = 1
    per_page = 100

    print(f"Fetching videos from Vimeo Folder ID: {folder_id} for User ID: {user_id}")
    while True:
        try:
            # CORRECTED ENDPOINT: Using /users/{user_id}/folders/{folder_id}/videos for Vimeo folders.
            # We're requesting basic fields: name (title), created_time (upload date), and uri (for ID).
            # FIX: Changed 'query' to 'params' for correct parameter passing.
            response = client.get(
                f'/users/{user_id}/folders/{folder_id}/videos',
                params={'page': page, 'per_page': per_page, 'fields': 'name,created_time,uri'}
            )
            response.raise_for_status() # Raise an HTTP error for bad responses
            data= response.json()
            videos_on_page = data.get('data', [])

            if not videos_on_page:
                break # no more videos

            all_videos.extend(videos_on_page)

            # check for more pages
            if data.get('paging', {}).get('next') is None:
                break # last page or fewer than per_page items

            page += 1
            print(f"Fetched page {page-1}, total videos so far: {len(all_videos)}")
        
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error fetching videos from album {album_id}: {e}")
            print(f"Response content: {e.response.text}")
            break
        except requests.exceptions.HTTPError as e:
            print(f"Connection error fetching videos from album {album_id}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred while fetching videos from folder {folder_id}: {e}")
            break
    print(f"Finished fetching videos. Total videos in album: {len(all_videos)}")
    return all_videos

def get_video_id_from_uri(uri: str) -> str | None:
    """
    Extracts the Vimeo video ID from its URI (e.g., "/videos/123456789").

    Args:
        uri (str): The Vimeo video URI.

    Returns:
        str | None: The extracted video ID as a string, or None if not found.
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

    Args:
        video_id (str): The ID of the Vimeo video.
        new_title (str): The new title for the video.

    Returns:
        bool: True if the title was updated successfully, False otherwise.
    """
    response = None
    payload = {
        'name': new_title # the 'name' field is used for the video title
    }
    try:
        # The PATCH method is used to update specific fields of a resource
        response.client.patch(f'/videos/{video_id}', data=payload)
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
    Main function to orchestrate scanning Vimeo album, fetching video info,
    and updating Vimeo video titles.
    """
    if not VIMEO_ACCESS_TOKEN:
        print("ERROR: VIMEO_ACCESS_TOKEN is not set. Please ensure it's in your .env file.")
        print("See instructions below for creating an .env file.")
        return
    if not VIMEO_FOLDER_ID:
        print("ERROR: VIMEO_FOLDER_ID is not set. Please ensure it's in your .env file.")
        print("See instructions below on how to create an .env file.")
        return

    # Get authenticated user's ID:
    authenticated_user_id = get_authenticated_user_id()
    if not authenticated_user_id:
        print("ERROR: Could not retrieve authenticated user ID. Please check your access token and its scopes.")
        return

    print(f"Authenticated User ID: {authenticated_user_id}")
    print(f"Starting Vimeo album processing for Album ID: {VIMEO_FOLDER_ID}")

    # fetch videos from the specified folder
    videos_in_folder = get_folder_videos(authenticated_user_id, VIMEO_FOLDER_ID) or []

    if not videos_in_folder:
        print(f"No videos found in folder {VIMEO_FOLDER_ID} or an error occurred. Exiting.")
        return
        
    processed_count = 0
    skipped_count = 0

    for i, video_info in enumerate(videos_in_folder):
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