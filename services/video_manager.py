import os
import cv2
from PIL import Image
from config.settings import VIDEOS_FOLDER


class VideoManager:
    def __init__(self):
        self.videos_folder = VIDEOS_FOLDER
        self.videos = []

    def get_videos(self) -> list:
        # self.videos = []
        files = []
        for file in os.listdir(self.videos_folder):
            if file.endswith(".mp4"):
                files.append(file)
        files.sort(
            key=lambda x: os.path.getmtime(os.path.join(self.videos_folder, x))
        )
        files.reverse()
        self.videos = files
        return self.videos

    def get_video_info(self, video_name) -> str:
        if video_name in self.videos:
            # getsize returns BYTES
            bytes_size = os.path.getsize(os.path.join(self.videos_folder, video_name))

            # Convert to MB
            mb_size = bytes_size / (1024 * 1024)

            # Format to 2 decimal places with the unit
            return f"{mb_size:.2f} MB"

        return "Unknown size"

    def get_thumbnail_in_memory(self, video_name) -> Image.Image | None:
        video_path = os.path.join(self.videos_folder, video_name)
        cap = cv2.VideoCapture(video_path)
        success, frame = cap.read()
        cap.release()

        if not success:
            return None

        # OpenCV uses BGR color order, but PIL/Tkinter uses RGB.
        # We MUST convert the color space.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the OpenCV array into a PIL Image object
        img = Image.fromarray(frame_rgb)

        # Optional: Resize it here to save RAM and match your UI
        img.thumbnail((160, 90))

        return img

    def delete_video(self, video_name, callback=None):
        video_path = os.path.join(self.videos_folder, video_name)
        if os.path.exists(video_path):
            os.remove(video_path)
        if callback:
            callback()
