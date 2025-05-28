from django.utils import timezone
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Tags(models.Model):
    value = models.TextField(max_length=20, unique=True)

    def __str__(self):
        return self.value

    def get_absolute_url(self):
        return reverse("game-detail", kwargs={"pk": self.pk})


class Game(models.Model):
    tags = models.ManyToManyField(Tags, related_name="games")
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to="games/thumbnails/",
        default="default_images/default_game.jpg",
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_count = models.IntegerField(
        default=0, validators=[MinValueValidator(0)], db_index=True
    )
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        db_index=True,
    )
    game_file = models.FileField(upload_to="games/", null=True, blank=True)
    game_file_win = models.FileField(
        upload_to="games/win_builds",
        null=True,
        blank=True,
    )
    webgl_index_path = models.CharField(max_length=255, blank=True, null=True)

    #     dont forget to add (progress, achievements)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("game-detail", kwargs={"pk": self.pk})


class GameComments(models.Model):
    game = models.ForeignKey(
        Game, related_name="comments", on_delete=models.CASCADE, db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="game_comments_user",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.game.title}"


class GameRating(models.Model):
    game = models.ForeignKey(
        Game, related_name="ratings", on_delete=models.CASCADE, db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="game_rating_user",
        on_delete=models.CASCADE,
        db_index=True,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
        db_index=True,
        default=1,
    )

    class Meta:
        unique_together = ["game", "user"]

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
        db_index=True,
    )
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    theme = models.CharField(
        max_length=200, help_text="theme of the game jam", db_index=True
    )
    prizes = models.TextField(max_length=200, blank=True, null=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="joined_game_jams", blank=True
    )
    submitted_games = models.ManyToManyField(
        "Game", related_name="game_jams", blank=True
    )
    game_jam_thumbnail = models.ImageField(
        upload_to="game_jams/thumbnails/",
        default="default_images/default_game.jpg",
        blank=True,
    )
    isOnline = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        super().clean()
        if not self.isOnline and not self.location:
            raise ValidationError(
                {"location": "Location is required for offline game jams."}
            )

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
