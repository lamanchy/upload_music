import threading

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import UploadedSong
from app.upload_song import upload_song

lock = threading.Lock()


@receiver(post_save, sender=UploadedSong, dispatch_uid='run_daemon')
def run_daemon(instance: UploadedSong, created, **kwargs):
    if created:
        if settings.DEBUG:
            upload_song(instance)
        else:
            t = threading.Thread(target=upload_song, args=(instance,))
            t.setDaemon(True)
            t.start()

        raise
