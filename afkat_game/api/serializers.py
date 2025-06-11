from django.contrib.auth import get_user_model
from rest_framework import serializers

from afkat.utils.serializer_field import CompressedImageField
from afkat_game.models import Game, GameComments, GameRating, Tags, GameJam
from afkat_game.services.game_jam_service import join_game_jam, leave_game_jam
from afkat_game.services.game_service import get_user_rating

User = get_user_model()


class GameCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'user.username')
    user_id = serializers.ReadOnlyField(source = 'user.id')

    class Meta:
        model = GameComments
        fields = ['id', 'game', 'user_id', 'username', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'username', 'created_at', 'updated_at']
        extra_kwargs = {
            'game': {'required': False},
        }


class GameRatingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'user.username')
    game = serializers.ReadOnlyField(source = 'game.title')

    class Meta:
        model = GameRating
        fields = ['game', 'username', 'rating']
        read_only_fields = ['user', 'username']


class GameDetailSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'creator.username')
    user_id = serializers.ReadOnlyField(source = 'creator.id')
    user_rating = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many = True,
        slug_field = "value",
        queryset = Tags.objects.all()
    )

    thumbnail = CompressedImageField(
        max_size = 1200,
        quality = 80,
        maintain_format = True,
        max_file_size_kb = 500
    )

    class Meta:
        model = Game
        fields = ['id', 'user_id', 'username', 'title', 'description', 'user_rating', 'tags','created_at','updated_at',
                  'download_count', 'rating', 'thumbnail', "game_file", 'game_file_win', 'webgl_index_path', ]
        read_only_fields = ['user_id','username', 'download_count', 'created_at', 'updated_at', 'webgl_index_path']
        extra_kwargs = {
            'rating': {'required': False},
        }

    def get_user_rating(self, obj):
        request = self.context.get('request')
        return get_user_rating(obj, request.user)

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class GameJamSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source = 'created_by.username')
    is_active = serializers.ReadOnlyField()
    participants_count = serializers.SerializerMethodField()
    participants = serializers.SlugRelatedField(
        many = True, read_only = True, slug_field = 'username'
    )

    class Meta:
        model = GameJam
        fields = [
            'id', 'title', 'description', 'created_by',
            'start_date', 'end_date', 'theme', 'prizes',
            'participants', 'participants_count',
            'is_active', 'game_jam_thumbnail', 'isOnline', 'location'
        ]
        read_only_fields = ["created_by"]

    def get_participants_count(self, obj):
        return obj.participants.count()

    def create(self, validate_data):
        validate_data['created_by'] = self.context['request'].user
        return super().create(validate_data)


class GameJamParticipationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices = ['join', 'leave'])

    def validate(self, data):
        if 'game_jam' not in self.context:
            raise serializers.ValidationError({"error": "GameJam context missing"})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        game_jam = self.context['game_jam']
        action = self.validated_data['action']

        if action == 'join':
            join_game_jam(user, game_jam)
        elif action == 'leave':
            leave_game_jam(user, game_jam)
