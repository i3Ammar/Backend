from django.contrib import admin
from afkat_home.models import  Post, Comment


# Register your models here.


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("slug", "published_at", "image")
    readonly_fields = ("created_at", "modified_at")


admin.site.register(Comment)
admin.site.register(Post, PostAdmin)
