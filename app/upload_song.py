import threading

from app.uploader import Uploader
from app.video_maker import VideoMaker
from app.models import UploadedSong

lock = threading.Lock()


def upload_song(song: UploadedSong):
    with lock:
        video_maker = VideoMaker(song)
        video_path = video_maker.create_video()

        uploader = Uploader(song, video_path)
        uploader.upload()
