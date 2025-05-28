from django.contrib import admin

from afkat_art.models import ArtModel, TagsModel, ArtComment, ArtRating

# Register your models here.

admin.site.register(ArtModel)
admin.site.register(ArtComment)
admin.site.register(ArtRating)
admin.site.register(TagsModel)
