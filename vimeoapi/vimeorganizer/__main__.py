from PyVimeo import VimeoClient
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Vimeo Client
client = VimeoClient(
    token=os.getenv('VIMEO_ACCESS_TOKEN'),
    key=os.getenv('VIMEO_CLIENT_IDENTIFIER'),
    secret=os.getenv('VIMEO_CLIENT_SECRET')
)

def get_team_library_videos():
    # Fetch all videos uploaded by the org.
    videos = []
    uri = '/me/videos'
    while uri:
        try:
            response = client.get(uri)
            data = response.json()
            videos.extend(data['data'])
            uri = data['paging'].get('next')
        except vimeo.exceptions.VimeoRequestError as e:
            print(f"Error fetching videos: {e}")
            break
    return videos

def get_existing_albums():
    # Fetch all existing albums (folders) on Vimeo.
    albums = {}
    uri = 'me/albums' # replace with correct uri
    while uri:
        try:
            response = client.get(uri)
            data = response.json()
            for album in data['data']:
                albums[album['name']] = album['uri']
            uri = data['paging'].get('next')
        except vimeo.exceptions.VimeoRequestError as e:
            logger.error(f"Error fetching albums: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    return albums

def add_video_to_album(video_uri, album_uri):
    """
    Add a video to an existing album.
    
    Args:
        video_uri (str): The URI of the video to add.
        album_uri (str): The URI of the album to add the video to.
    """
    try:
        response = client.put(f"{album_uri}/videos/{video_uri.split('/')[-1]}")
        if response.status_code == 204:
            logger.info(f"Video {video_uri} added to album {album_uri}")
        else:
            logger.info(f"Failed to add video {video_uri} to album {album_uri}, Status code: {response.status_code}")
    except vimeo.exceptions.VimeoRequestError as e:
        logger.error(f"Error adding video to album: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")           

def organize_team_library_videos():
    # Organize videos from the Team Library into existing albums based on video names
    videos = get_team_library_videos()
    albums = get_existing_albums()

    for video in videos:
        video_name = video['name']
        video_uri = video['uri']

        # match video to album name
        # test and customize logic based on naming conventions
        album_name = video_name.split()[0] # Example: use the first word as the album name

        if album_name in albums:
            add_video_to_album(video_uri, albums[album_name])
        else:
            print(f"No matching album found for video: {video_name}")

# Run
if __name__ == "__main__":
    organize_team_library_videos()