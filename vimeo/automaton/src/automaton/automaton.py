import os
import requests
from datetime import datetime

try:
    from PyVimeo import VimeoClient
except ImportError:
    print("The 'vimeo' Python library is not installed")
    print("Please install it using: pip install vimeo")
    print("Exiting script.")
    exit()

VIMEO_ACCESS_TOKEN = 'e0419ec0737d3e53be6577710225629b'
VIMEO_ALBUM_ID = '25750561'
DATE_FORMAT = "%Y-%m-%d"

client = VimeoClient(
    token=VIMEO_ACCESS_TOKEN,
    key='dc7bd89bb360139476293896b2196c39dd4c56b6',
    secret='t4o1k2fZ5m2DeQnXcAEcsoB2K7ZRuhLMReqoZGbBbniGrNBK1ZsqePKS6hZ4YQIXqfR34ZqhhSiry1O2mAlwhdDcNlFM5iNDtEfa27AbYnUk3qcJof8/+PEzK/45Lo3E'
)

def get_album_videos(album_id: str) -> list[dict]:
    """
    Fetches all videos within a specific Vimeo album. Handles pagination.

    Args:
        album_id (str): The ID of the Vimeo album.

    Returns:
        list[dict]: A list of dictionaries, each containing video information.
                    Returns an empty list if an error occurs or no videos are found.
    """
    all_videos = []
    page = 1
    per_page = 100

    print(f"Fetching videos from Vimeo Album ID: {album_id}")
    while True:
        try:
            response = client.get(
                f'/album/{album_id}/videos',
                query={'page': page, 'per_page': per_page, 'fields': 'name,created_time,uri'}
            )
            response.raise_for_status() # Raise an HTTP error for bad responses
            data= response.json()
            videos_on_page = data.get('data', [])

            if not videos_on_page:
                break # no more videos

            all_videos.extend(videos_on_page)

            # check for more pages
            if len(videos_on_page) < per_page:
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
            print(f"An unexpected error occurred while fetching videos from album {album_id}: {e}")
            break
    print(f"Finished fetching videos. Total videos in album: {len(all_videos)}")

def get_video_from_url(uri: str) -> str | None:
    """
    Extracts the Vimeo video ID from its URI (e.g., "/videos/123456789").

    Args:
        uri (str): The Vimeo video URI.

    Returns:
        str | None: The extracted video ID as a string, or None if not found.
    """
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
        print(f"HTTP error updating video title for ID {video_id}: {e}")
        print(f"Response content: {e.response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error updating video title for ID {video_id}: {e}")
    return False

def main():
    """
    Main function to orchestrate scanning Vimeo album, fetching video info,
    and updating Vimeo video titles.
    """
    if VIMEO_ACCESS_TOKEN == 'e0419ec0737d3e53be6577710225629b':
        print("ERROR: please replace your 'VIMEO_ACCESS_TOKEN' with correct token.")
        return
    if VIMEO_ALBUM_ID == 'YOUR_VIMEO_ALBUM_ID':
        print("ERROR: Please replace 'YOUR_VIMEO_ALBUM_ID' with the actual ID of your Vimeo album.")
        return
    print(f"Starting Vimeo album processing for Album ID: {VIMEO_ALBUM_ID}")

    videos_in_album = get_album_videos(VIMEO_ALBUM_ID)

    if not videos_in_album:
        print(f"No videos found in album {VIMEO_ID_ALBUM} or an error occurred. Exiting.")
    
    processed_count = 0
    skipped_count = 0

    for i, video_info in enumerate(videos_in_album):
        video_uri = video_info.get('uri')
        current_title = video_info.get('name')
        upload_date_str = video_info.get('created_time')

        if not video_uri:
            print(f"\nVideo {i+1}: Missing URI in video info. Skipping.")
            skipped_count += 1
            continue

        video_id = get_video_id_from_uri(video_url)
        if not video_id:
            print(f"\nVideo {i+1} (URI: {video_url}): Could not extract video ID from URI. SKipping.")
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