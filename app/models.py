from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, FileField


class UploadedSong(Model):
    name = CharField(max_length=128)
    author = CharField(max_length=128)
    file = FileField(upload_to='records')

    def clean(self):
        if not self.file.name.endswith('m4a') and not self.file.name.endswith('mp3'):
            raise ValidationError('not .mp3 or .m4a')

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'id',
