import customtkinter
from models.video import Video


class VideoItem(customtkinter.CTkFrame):
    def __init__(self, parent, video: Video, delete_callback, min_height=80):
        super().__init__(parent, corner_radius=10, height=min_height)

        # methods
        self.delete_callback = delete_callback

        # variables
        self.video = video

        # Configure grid to let the detail section expand
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)  # Ensures the frame respects 'height'

        # Updated sizes
        thumb_w = 180
        thumb_h = 100

        # 1. Update the image scaling
        self.thumbnail_image = customtkinter.CTkImage(
            light_image=video.image,
            dark_image=video.image,
            size=(thumb_w, thumb_h)
        )

        # 2. Update the label container
        self.image_box = customtkinter.CTkLabel(
            self,
            image=self.thumbnail_image,
            text="",
            width=thumb_w,
            height=thumb_h,
            corner_radius=12  # Increased radius for a smoother look
        )

        self.image_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")

        # Text Info Container
        self.video_detail_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.video_detail_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.video_detail_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = customtkinter.CTkLabel(
            self.video_detail_frame,
            text=video.title,
            anchor="w",
            font=customtkinter.CTkFont(size=13, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="new")

        # Metadata (Size)
        self.size_label = customtkinter.CTkLabel(
            self.video_detail_frame,
            text=f"Size: {video.size}",
            anchor="w",
            font=customtkinter.CTkFont(size=11),
            text_color="gray70"
        )
        self.size_label.grid(row=1, column=0, sticky="sew")

        self.delete_button = customtkinter.CTkButton(
            self.video_detail_frame,
            text="Delete Video",
            fg_color="#D22B2B",  # A nice "Berry" red for the button body
            hover_color="#8B0000",  # A darker red when the mouse is over it
            border_color="#721c24",  # A very dark red border
            border_width=1,
            corner_radius=15,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            command=self.confirm_delete
        )
        self.delete_button.grid(row=2, column=0, sticky="e")

    def confirm_delete(self):
        self.destroy()
        self.delete_callback(self.video.title)
