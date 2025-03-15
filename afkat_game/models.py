import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Asset(models.Model):
    title = models.CharField(max_length = 200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'assets')
    file = models.FileField(upload_to = 'assets/')
    preview_image = models.ImageField(upload_to = 'asset_previews/', blank = True, null = True)
    category = models.CharField(max_length = 100)

    def __str__(self):
        return self.title


class Game(models.Model):
    title = models.CharField(max_length = 200, db_index = True)
    description = models.TextField()
    game_file = models.FileField(upload_to = 'games/')
    thumbnail = models.ImageField(upload_to = 'thumbnails/', null = True, blank = True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    download_count = models.IntegerField(default = 0)
    rating = models.FloatField(default = 0, validators = [MinValueValidator(0), MaxValueValidator(5)])

    #     dont forget to add (progress, achievements)

    def __str__(self):
        return self.title


# class Contest(models.Model):
#     title = models.CharField(max_length = 200)
#     description = models.TextField()
#     comments = models.TextField(blank = True)
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add = True)
#     updated_at = models.DateTimeField(auto_now = True)
#     contest_id = models.UUIDField(default = uuid.uuid4, editable = False, unique = True)
#
#     def __str__(self):
#         return self.title


class GameJam(models.Model):
    title = models.CharField(max_length = 200 , db_index = True)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE,
                                   related_name = 'game_jams_created_by')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    theme = models.CharField(max_length = 200 , help_text = "theme of the game jam")
    prizes = models.TextField(blank = True)
    contest_id = models.UUIDField(default = uuid.uuid4, editable = False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name = 'participating_in_jams',
                                          blank = True)

    def __str__(self):
        return self.title
