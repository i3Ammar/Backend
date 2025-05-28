from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class TagsModel(models.Model):
    value = models.TextField(max_length = 20, unique = True)

    def __str__(self):
        return self.value


class ArtModel(models.Model):
    title = models.CharField(max_length = 20, db_index = True)
    description = models.TextField(blank = True)
    thumbnail = models.ImageField(
        upload_to = "art_thumbnails/",
        default = "default_images/default_art.jpg",
        null = True,
        blank = True,
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    model_file = models.FileField(
        upload_to = "3d_models/", help_text = ("Upload 3D files (.obj ,.fbx,.glb ,.gltf)")
    )
    tags = models.ManyToManyField(
        TagsModel, related_name = "art_tags", help_text = "Comma-seperated tags."
    )
    rating = models.FloatField(
        default = 0.0,
        validators = [MinValueValidator(1.0), MaxValueValidator(5.0)],
        db_index = True,
    )
    created_at = models.DateTimeField(auto_now_add = True)
    download_count = models.IntegerField(default = 0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ArtComment(models.Model):
    art = models.ForeignKey(
        ArtModel, related_name = "comments", on_delete = models.CASCADE, db_index = True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = "art_comments",
        on_delete = models.CASCADE,
        db_index = True,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.art.title}"


class ArtRating(models.Model):
    art = models.ForeignKey(
        ArtModel, related_name = "ratings", on_delete = models.CASCADE, db_index = True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = "art_rating",
        on_delete = models.CASCADE,
        db_index = True,
    )
    rating = models.PositiveSmallIntegerField(
        validators = [MinValueValidator(1), MaxValueValidator(5)],
        help_text = "Rating from 1 to 5",
        db_index = True,
        default = 1,
    )

    class Meta:
        unique_together = ["art", "user"]


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        art = self.art
        art.rating = ArtRating.objects.filter(art=art).aggregate(
            models.Avg("rating")
        )["rating__avg"]
        art.save(update_fields=["rating"])

    def __str__(self):
        return f"{self.user.username} rated {self.art.title}: {self.rating}/5"
