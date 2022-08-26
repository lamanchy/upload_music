from django.db.models import Model, CharField, FileField


class UploadedSong(Model):
    name = CharField(max_length=128)
    file = FileField(upload_to='records')

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'id',
