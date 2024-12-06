import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class VideoHandler(FileSystemEventHandler):
    def on_created(self,event):
        if event.src_path.endswith(".mp4"):
            print(f"New video detected:{event.src_path}")

def monitor_directory(directory):
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive =False)
    observer.start()
    print(f"Monitor Directory:{directory}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
if __name__ == "__main__":
    videos_dir = os.path.join(os.getcwd(), "videos")
    os.makedirs(videos_dir, exist_ok=True)
    monitor_directory(videos_dir)