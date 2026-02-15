import os

source_dir = os.path.expanduser("~/Downloads")
VIDEOS_FOLDER = os.path.join(source_dir, "Youtube Videos")


class AppSettings:
    def __init__(self):
        self.title = "YouTube Downloader"
        self.geometry = "1000x600"
