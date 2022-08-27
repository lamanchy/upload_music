from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpResponseRedirect

from app.models import UploadedSong
from app.upload_song import upload_song


@admin.register(UploadedSong)
class UploadedSongAdmin(ModelAdmin):

    def response_add(self, request, obj, post_url_continue=None):
        auth_url = upload_song(obj)

        return HttpResponseRedirect(auth_url)
