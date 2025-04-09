from rest_framework import serializers

from afkat_game.models import Game, GameComments, GameRating, Tags


class GameCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'user.username')
    class Meta:
        model = GameComments
        fields = ['id','game','user','username','content','created_at','updated_at']
        read_only_fields = ['user','username', 'created_at', 'updated_at']

class GameRatingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'user.username')

    class Meta :
        model = GameRating
        fields = ['id','game','user','username','rating','created_at']
        read_only_fields = ['user','username','created_at']

class GameDetailSerializer (serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source = 'user.username')
    user_rating = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many = True ,
        slug_field = "value" ,
        queryset = Tags.objects.all()
    )

    class Meta :
        model = Game
        fields =  "__all__"
        read_only_field = ['download_count' ]
        extra_kwargs = {
            'rating':{'required':False}
        }


    def get_user_rating(self , obj ):
        request = self.context.get('request')
        if request and request.user.is_authenticated :
            try :
                rating = GameRating.objects.get(game=obj ,user  = request.user)
                return rating.rating
            except GameRating.DoesNotExist:
                return None
        return None





