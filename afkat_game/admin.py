from django.contrib import admin
# Register your models here.
from .models import Game

class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'download_count', 'rating')
    list_filter = ('creator', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'rating', 'created_at', 'updated_at')
    
admin.site.register(Game, GameAdmin)
