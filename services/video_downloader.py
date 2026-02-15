import os
import yt_dlp


class VideoDownloader:
    def __init__(self, video_url: str):
        self.video_url = video_url
        self.info_dict = None  # Stores video metadata after extraction

    def _fetch_info(self):
        """Fetches video metadata if not already loaded."""
        if self.info_dict is None:
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.info_dict = ydl.extract_info(self.video_url, download=False)

    def download(self, progress_callback):
        # This hook runs inside the yt-dlp process
        def internal_hook(d):
            if d['status'] == 'downloading':
                # Try to get total size from exact key or estimate
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)

                if total:
                    percentage = downloaded / total
                    # Send the 0.0 - 1.0 value back to the UI
                    progress_callback(percentage)

            elif d['status'] == 'finished':
                progress_callback(1.0)

        source_dir = os.path.expanduser("~/Downloads")
        videos_folder = os.path.join(source_dir, "Youtube Videos")
        os.makedirs(videos_folder, exist_ok=True)

        ydl_opts = {
            'format': 'best[height<=720]/best',
            'outtmpl': os.path.join(videos_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [internal_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.video_url])

    def get_video_image(self):
        self._fetch_info()
        return self.info_dict.get('thumbnail')

    def get_video_title(self):
        self._fetch_info()
        return self.info_dict.get('title')
