class Video:
    def __init__(self, title, size, file_path, image):
        self.title = title
        self.size = size
        self.file_path = file_path
        self.image = image

    def __str__(self):
        return str(self.title)
