# afkat_game/services/game_service.py

from afkat_game.models import GameRating
from rest_framework import serializers

def get_user_rating(game, user):
    if user.is_authenticated:
        try:
            rating = GameRating.objects.get(game=game, user=user)
            return rating.rating
        except GameRating.DoesNotExist:
            return None
    return None

def validate_cover_image(self , value):
    if value.size > 5*1024*1024:
        raise serializers.ValidationError('Image too large')

    valid_extensions = ['jpg', 'jpeg', 'webp', 'png']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise serializers.ValidationError(f'Unsupported file extension.  Use: {', '.join(valid_extensions)}')

def validate_game_file(self , value):
    if value.size > 1024*1024*1024:
        raise serializers.ValidationError('Game file too large')
    valid_extensions = ['zip', 'rar','7z']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise serializers.ValidationError(f'Unsupported file extension.  Use: {', '.join(valid_extensions)}')

    return value
