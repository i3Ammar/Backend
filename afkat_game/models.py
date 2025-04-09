import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Tags(models.Model):
    value = models.TextField(max_length=20, unique=True)

    def __str__(self):
        return self.value


# Create your models here.
class Asset(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assets"
    )
    file = models.FileField(upload_to="assets/")
    preview_image = models.ImageField(
        upload_to="asset_previews/", blank=True, null=True
    )
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Game(models.Model):
    tags = models.ManyToManyField(Tags, related_name = "games" )
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    game_file = models.FileField(upload_to="games")
    thumbnail = models.ImageField(upload_to="games/thumbnails/", null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_count = models.IntegerField(default=0 , validators = [MinValueValidator(0)])
    rating = models.FloatField(default = 0.0 , validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    #     dont forget to add (progress, achievements)

    def __str__(self):
        return self.title


class GameComments(models.Model):
    game = models.ForeignKey(Game, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="game_comments", on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.game.title}"


class GameRating(models.Model):
    game = models.ForeignKey(Game, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="game_rating", on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["game", "user"]

    ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.game.title}: {self.rating}/5"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        game = self.game
        avg_rating = GameRating.objects.filter(game=game).aggregate(
            models.Avg("rating")
        )["rating__avg"]
        game.rating = avg_rating
        game.save(update_fields=["rating"])


class GameJam(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_jams_created_by",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    theme = models.CharField(max_length=200, help_text="theme of the game jam")
    prizes = models.TextField(blank=True, null=True)
    contest_id = models.UUIDField(default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participating_in_jams", blank=True
    )

    def __str__(self):
        return self.title
