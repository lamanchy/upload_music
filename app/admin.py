from django.contrib import admin
from django.contrib.admin import ModelAdmin

from app.models import UploadedSong


@admin.register(UploadedSong)
class UploadedSongAdmin(ModelAdmin):
    pass
