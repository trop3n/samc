import pyvimeo
import dotenv

# Config
VIMEO_CLIENT_ID = 'YOUR_CLIENT_ID'
VIMEO_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
VIMEO_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
SOURCE_FOLDER_ID = 'SOURCE_FOLDER_ID'

def get_all_videos(vimeo_client, folder_id):
    """Retrieve all videos from a specified folder."""
    videos = []
    page = 1
    while True:
        response = vimeo_client.get(f'/me/folder/{folder_id}/videos', params={"page": page, 'per_page': 100})
        if response.status_code != 200:
            print(f"Error retrieving videos: {response.json().get('error')}")
            break
        data = response.json()
        videos.extend(data.get('data', []))
        if not data.get('paging', {}).get('next'):
            break
        page += 1
    return videos

def get_or_create_folder(vimeo_client, folder_path):
    """Get or create folders based on a path (e.g. 'parent/child')."""
    current_parent_id = None
    for folder_name in folder_path.split('/'):
        # fetch existing folders
        if current_parent_id:
            response = vimeo_client.get(f"/me/folders/{current_parent_id}/folders")
        else:
            response = vimeo_client.get('/me/folders', params={'per_page': 100})
        
        if response.status_code != 200:
            raise Exception(f'Failed to fetch folders: {response.json().get('error')}')

        existing_folders = response.json().get('data', [])
        target_folder = next((f for f in existing_folders if f['name'] == folder_name), None)

        if not target_folder:
            # create the folder
            data ={'name': folder_name}
            if current_parent_id:
                response = vimeo_client.post(f'/me/folders/{current_parent_id}/folders', data=data)

            else:
                response = vimeo_client.post('/me/folders', data=data)

            if response.status_code not in (200, 201):
                raise Exception(f"failed to create folder '{folder_name}: {response.json().get('error')}")
            target_folder = response.json()
        
        current_parent_id = target_folder['uri'].split('/')[-1]
    return current_parent_id

    def main():
        # init vimeo client
        vimeo = pyvimeo.VimeoClient(
            token=VIMEO_ACCESS_TOKEN,
            key=VIMEO_CLIENT_ID,
            secret=VIMEO_CLIENT_SECRET
        )

        # fetch all videos from the source folder
        videos = get_all_videos(vimeo, SOURCE_FOLDER_ID)
        print(f"Found {len(videos)} videos in source folder.")

        for video in videos:
            video_id = video['uri'].split('/')[-1]
            title = video['name'].lower()

            # Determine destination folder based on title
            if 'capture' in title:
                dest_path = 'Social Group Ministries/The Root'
            elif 'class' in title:
                dest_path = "Scott's Classes"
            elif 'Contemporary' in title or 'Traditional' in title:
                dest_path = "Worship Services"
            else:
                print(f"Skipping '{video['name']} (no matching keywords)")
                continue

            # get or create the destination folder:
            try:
                folder_id = get_or_create_folder(vimeo, dest_path)
            except Exception as e:
                print(f"Error processing '{video['name']}': {str(e)}")
                continue

            # move videos
            response = vimeo.patch(
                f'/videos/{video_id}',
                data = {'folder_uri': f'/folders/{folder_id}'}
            )
            if response.status_code == 200:
                print(f"Moved '{video['name']}' to '{dest_path}'")
            else:
                print(f"Failed to move {video['name']}': {response.json().get('error')}")

if __name__ == "__main__":
    main()