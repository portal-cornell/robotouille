import cv2

class VideoWriterContext:
    def __init__(self, filename, fourcc, fps, frame_size):
        self.filename = filename
        self.fourcc = fourcc
        self.fps = fps
        self.frame_size = frame_size
        self.writer = None

    def __enter__(self):
        self.writer = cv2.VideoWriter(self.filename, self.fourcc, self.fps, self.frame_size)
        if not self.writer.isOpened():
            raise ValueError("VideoWriter could not be opened.")
        return self.writer

    def __exit__(self, exc_type, exc_value, traceback):
        if self.writer is not None:
            self.writer.release()

def record_video(imgs, filename, fourcc_str, fps):
    """Records a video from a list of images.
    
    Parameters:
        imgs (List[np.array]):
            The list of RGB images to record.
        filename (str):
            The filename of the video.
        fourcc_str (str):
            The 4-char code for the video codec to use.
        fps (int):
            The frames per second of the video.
    """
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
    height, width, _ = imgs[0].shape
    frame_size = (width, height)
    imgs = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in imgs] # Convert RGB to cv2 BGR for correct colors
    with VideoWriterContext(filename, fourcc, fps, frame_size) as video:
        for img in imgs:
            video.write(img)