import threading

from app.models import UploadedSong
from app.uploader import Uploader
from app.video_maker import VideoMaker

lock = threading.Lock()


def do_upload_song(song, uploader):
    uploader.handle_async_auth()
    with lock:
        video_maker = VideoMaker(song)
        video_path = video_maker.create_video()
        uploader.upload(song, video_path)


def upload_song(song: UploadedSong):
    uploader = Uploader()

    t = threading.Thread(target=do_upload_song, args=(song, uploader))
    t.setDaemon(True)
    t.start()

    return uploader.auth_url
