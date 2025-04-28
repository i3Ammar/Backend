from django.contrib import admin

from afkat_art.models import ArtModel, TagsModel

# Register your models here.

admin.site.register(ArtModel)
admin.site.register(TagsModel)
