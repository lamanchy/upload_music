from django.core.exceptions import ValidationError
from django.db.models import Model, CharField, FileField, DateField


class UploadedSong(Model):
    name = CharField(max_length=128)
    author = CharField(max_length=128)
    file = FileField(upload_to='records')
    created_at = DateField(auto_now=True)

    # def clean(self):
    #     if not self.file.name.endswith('m4a') and not self.file.name.endswith('mp3'):
    #         raise ValidationError('not .mp3 or .m4a')

    def __str__(self):
        return self.title

    class Meta:
        ordering = 'id',

    @property
    def title(self):
        name = f'{self.author} - {self.name}'
        if self.author != 'Blonďák':
            name += ' (cover)'

        return name

    @property
    def description(self):
        return f'{self.created_at.day}. {self.created_at.month}. {self.created_at.year}'
