import os
import requests
import hashlib
import logging
from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from tqdm import tqdm
import asyncio
import threading
import random
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Load environment variables from .env file
load_dotenv()

# Get credentials and API token from environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
FLIC_TOKEN = os.getenv("FLIC_TOKEN")
MONITORED_DIR = os.getenv("MONITORED_DIR", os.path.join(os.getcwd(), "videos"))

# Ensure monitored directory exists
os.makedirs(MONITORED_DIR, exist_ok=True)

# Function to get FLIC Token dynamically if not provided in .env
def get_flic_token(username, password):
    url = "https://api.socialverseapp.com/user/token"
    params = {"username": username, "password": password}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        token = response.json().get("token")
        logging.info(f"Token obtained: {token}")
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch token: {e}")
        return None

# Initialize the FLIC_TOKEN dynamically if not already set in .env
if not FLIC_TOKEN:
    if not USERNAME or not PASSWORD:
        logging.critical("Username, password, or token not found in environment variables.")
        exit(1)
    FLIC_TOKEN = get_flic_token(USERNAME, PASSWORD)
    if not FLIC_TOKEN:
        logging.critical("Exiting: Unable to fetch FLIC token.")
        exit(1)

# Function to generate hash for a file
def generate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Global asyncio event loop
event_loop = asyncio.new_event_loop()

class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".mp4"):
            logging.info(f"New video detected: {event.src_path}")
            asyncio.run_coroutine_threadsafe(upload_video(event.src_path), event_loop)

async def monitor_directory(directory):
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    logging.info(f"Monitoring Directory: {directory}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping directory monitoring.")
        observer.stop()
        observer.join()

async def get_upload_url(file_path):
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    params = {
        "file_name": os.path.basename(file_path),
        "file_type": "video/mp4"
    }

    logging.info(f"Requesting upload URL for {file_path} with headers: {headers} and params: {params}")

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(
                "https://api.socialverseapp.com/posts/generate-upload-url",
                headers=headers,
                params=params,
                timeout=10
            )
            logging.info(f"Response Status Code: {response.status_code}")
            response.raise_for_status()

            # Log the full response for debugging
            response_json = response.json()
            logging.info(f"Full Response: {response_json}")

            # Get the correct URL key from the response
            upload_url = response_json.get("url")
            if upload_url:
                logging.info(f"Upload URL obtained: {upload_url}")
                return upload_url
            else:
                logging.error("No upload URL returned in the response.")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Failed to get upload URL. Error: {e}")
            if attempt < 2:  # Wait and retry
                await asyncio.sleep(2 ** attempt)
            else:
                logging.critical("All retries failed.")
                return None

async def upload_video(file_path):
    upload_url = await get_upload_url(file_path)
    if not upload_url:
        return

    total_size = os.path.getsize(file_path)
    with tqdm(total=total_size, unit="B", unit_scale=True, desc="Uploading") as pbar:
        with open(file_path, "rb") as video_file:
            try:
                response = requests.put(upload_url, data=video_file, timeout=60)
                pbar.update(total_size)
                response.raise_for_status()
                logging.info(f"Uploaded successfully: {file_path}")
                await create_post(file_path)
                os.remove(file_path)
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to upload: {e}")

def generate_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to avoid memory issues with large files
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    return hasher.hexdigest()


def create_post():
    # Generate a hash from the actual uploaded file (use the path of the uploaded video)
    video_path = 'D:\\FreeLancing\\Video Bot\\Video-Search-and-Upload-Bot-Assignment\\videos\\new.mp4'
    video_hash = generate_hash(video_path)
    
    if video_hash is None:
        logging.error("Failed to generate video hash.")
        return

    # Generate a random category ID
    category_id = random.randint(1, 1000)

    # Create a video title
    video_title = f"Video_{random.randint(1000, 9999)}"

    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    body = {
        "title": video_title,
        "hash": video_hash,
        "is_available_in_public_feed": False,
        "category_id": category_id
    }

    logging.info(f"Creating post with body: {json.dumps(body)}")

    response = requests.post(
        "https://api.socialverseapp.com/posts",
        headers=headers,
        json=body
    )

    logging.info(f"Response Status Code: {response.status_code}")
    try:
        response_data = response.json()
    except ValueError:
        response_data = response.text  # Handle non-JSON responses

    if response.status_code == 400:
        logging.error(f"Bad Request: {response_data}")
    elif response.status_code == 201:
        logging.info("Post created successfully.")
    else:
        logging.error(f"Unexpected status code: {response.status_code} - {response_data}")

if __name__ == "__main__":
    threading.Thread(target=event_loop.run_forever, daemon=True).start()
    asyncio.run(monitor_directory(MONITORED_DIR))
