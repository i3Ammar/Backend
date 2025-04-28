from django.conf import settings
from django.db import models


# Create your models here.
class TagsModel(models.Model):
    value = models.TextField(max_length = 20, unique = True)

    def __str__(self):
        return self.value


class ArtModel(models.Model):
    title = models.CharField(max_length = 20, db_index = True)
    description = models.TextField(blank = True)
    thumbnail = models.ImageField(default = 'default_images/default_art.jpg', upload_to = "art_thumbnails/",
                                  null = True, blank = True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    model_file = models.FileField(
        upload_to = '3d_models/',
        help_text = (
            'Upload 3D files (.obj ,.fbx,.glb ,.gltf , .stl,)'
        )
    )
    preview_image = models.ImageField(
        upload_to = '3d_previews/',
        blank = True,
        null = True,
        help_text = 'Upload a preview image for the 3D model.'
    )
    tags = models.ManyToManyField(TagsModel, related_name = "art_tags", help_text = 'Comma-seperated tags.')
    created_at = models.DateTimeField(auto_now_add = True)
    download_count = models.IntegerField(default = 0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
