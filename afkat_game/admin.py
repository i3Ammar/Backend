from django.contrib import admin
# Register your models here.
from .models import Game, GameRating, GameComments, GameJam ,Tags


class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'download_count', 'rating')
    list_filter = ('creator', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'rating', 'created_at', 'updated_at')
    
admin.site.register(Game, GameAdmin)
admin.site.register(Tags)
admin.site.register(GameRating)
admin.site.register(GameComments)
admin.site.register(GameJam)
