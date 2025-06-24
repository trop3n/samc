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