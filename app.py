import customtkinter
import threading

from config.settings import AppSettings
from models.video import Video
from services.video_downloader import VideoDownloader
from services.video_manager import VideoManager
from widgets.video_item import VideoItem


class App(customtkinter.CTk):
    def __init__(self, settings: AppSettings, video_manager: VideoManager):
        super().__init__()

        self.video_manager = video_manager

        # Theme configuration
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")

        self.title(settings.title)
        self.geometry(settings.geometry)

        # Main Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Content Frame ---
        self.content_frame = customtkinter.CTkFrame(self, corner_radius=15)
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Header (Row 0)
        self.label = customtkinter.CTkLabel(
            self.content_frame, text="YouTube Downloader",
            font=customtkinter.CTkFont(size=25, weight="bold")
        )
        self.label.grid(row=0, column=0, pady=(30, 10))

        # URL Input (Row 1)
        self.url_input = customtkinter.CTkEntry(
            self.content_frame, placeholder_text="Paste YouTube URL here...", width=450, height=40
        )
        self.url_input.grid(row=1, column=0, padx=40, pady=10)

        # Download Button (Row 2)
        self.submit_button = customtkinter.CTkButton(
            self.content_frame, text="Download Video", width=150, height=35,
            command=self.download_video
        )
        self.submit_button.grid(row=2, column=0, pady=10)

        # Progress Container (Row 3 - Initially hidden)
        self.progress_container = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
        self.progress_container.grid_columnconfigure(0, weight=1)  # Let the bar expand
        self.progress_bar = customtkinter.CTkProgressBar(
            self.progress_container, width=400, height=25, corner_radius=10
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.progress_bar_label = customtkinter.CTkLabel(
            self.progress_container,
            text="0%",
            text_color="white",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            fg_color="transparent"  # Explicitly internal transparent
        )
        self.progress_bar_label.grid(row=0, column=1, padx=10)

        # Error/Status Label (Row 4)
        self.error_label = customtkinter.CTkLabel(
            self.content_frame, text="", font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.error_label.grid(row=4, column=0, pady=5)

        # History Label (Row 5)
        self.downloaded_label = customtkinter.CTkLabel(
            self.content_frame, text="Download History",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        self.downloaded_label.grid(row=5, column=0, pady=(10, 5), padx=25, sticky="w")

        # Scrollable List (Row 6)
        self.downloaded_videos_frame = customtkinter.CTkScrollableFrame(
            self.content_frame, fg_color="transparent"
        )
        self.downloaded_videos_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.downloaded_videos_frame.grid_columnconfigure(0, weight=1)

        # Make the scrollable list expand to fill remaining space
        self.content_frame.grid_rowconfigure(6, weight=1)

        self.load_videos()

    def load_videos(self):
        # Clear existing widgets
        for widget in self.downloaded_videos_frame.winfo_children():
            widget.destroy()

        videos = self.video_manager.get_videos()

        if not videos:
            no_video_label = customtkinter.CTkLabel(
                self.downloaded_videos_frame, text="No videos downloaded yet",
                text_color="gray", font=customtkinter.CTkFont(size=16)
            )
            no_video_label.grid(row=0, column=0, pady=40)
        else:
            for index, video_title in enumerate(videos):
                video_info = self.video_manager.get_video_info(video_title)
                video_img = self.video_manager.get_thumbnail_in_memory(video_title)

                video_obj = Video(video_title, video_info, video_title, video_img)

                item = VideoItem(self.downloaded_videos_frame, video_obj, self.hand_video_obj, min_height=100)
                item.grid(row=index, column=0, sticky="ew", padx=5, pady=5)

    def hand_video_obj(self, video_obj):
        # Using a thread for deletion to keep UI snappy
        def delete_task():
            self.video_manager.delete_video(video_obj)
            self.after(0, self.load_videos)

        threading.Thread(target=delete_task, daemon=True).start()

    def download_video(self):
        url = self.url_input.get().strip()
        if url:
            self.submit_button.configure(state="disabled")
            self.progress_container.grid(row=3, column=0, pady=10)  # Show using grid, NOT pack
            self.progress_bar.set(0)
            self.progress_bar_label.configure(text="0%", text_color="white")

            download_thread = threading.Thread(target=self._run_download, args=(url,), daemon=True)
            download_thread.start()
        else:
            self.show_error("Please enter a valid URL")

    def _run_download(self, url):
        try:
            downloader = VideoDownloader(url)
            # The downloader must call this progress_callback with a float 0.0-1.0
            downloader.download(progress_callback=lambda p: self.after(0, self.update_ui, p))
            self.after(0, self.on_download_finished)
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Error: {str(e)}"))
            self.after(0, lambda: self.submit_button.configure(state="normal"))

    def update_ui(self, value):
        self.progress_bar.set(value)
        percentage = int(value * 100)
        self.progress_bar_label.configure(text=f"{percentage}%")
        # Switch text color for visibility as bar fills
        # if percentage > 50:
        #     self.progress_bar_label.configure(text_color="black")

    def on_download_finished(self):
        self.progress_container.grid_forget()  # Hide the bar
        self.submit_button.configure(state="normal")
        self.url_input.delete(0, 'end')
        self.label.configure(text="Download Complete!", text_color="green")
        self.after(2000, lambda: self.label.configure(text="YouTube Downloader", text_color="white"))
        self.load_videos()

    def show_error(self, message: str):
        self.error_label.configure(text=message, text_color="red")
        self.after(3000, lambda: self.error_label.configure(text=""))


if __name__ == '__main__':
    app_settings = AppSettings()
    video_manager = VideoManager()
    app = App(app_settings, video_manager)
    app.mainloop()
