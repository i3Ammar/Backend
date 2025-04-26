from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from afkat_auth.models import User, Follow
from afkat_auth.serializers import UserProfileSerializer, FollowSerializer


# Create your views here.

@login_required
def profile(request):
    return render(request, "afkat_auth/profile.html")


class UserDetail(generics.RetrieveAPIView, ):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    @method_decorator(cache_page(5 * 60))
    def get(self, *args, **kwargs):
        return super(UserDetail, self).get(*args, **kwargs)


#

class FollowUserView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def create(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user_to_follow = get_object_or_404(User, pk = pk)
        follower = request.user

        if follower == user_to_follow:
            return Response(
                {"detail": "You cannot follow yourself."},
                status = status.HTTP_400_BAD_REQUEST
            )

        follow_instance, created = Follow.objects.get_or_create(
            follower = follower,
            defaults = {'following': user_to_follow},
            following = user_to_follow
        )
        if created:
            headers = self.get_success_headers(self.get_serializer(follow_instance).data)
            return Response(
                {'detail': f"You are now following {user_to_follow.username}"},
                status = status.HTTP_201_CREATED,
                headers = headers
            )
        else:
            return Response(
                {'detail': f'You are already following {user_to_follow.username}'},
                status = status.HTTP_200_OK,
            )


class UnfollowUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def get_object(self ):
        following_pk = self.kwargs.get('pk')
        user_to_unfollow = get_object_or_404(User , pk = following_pk)
        follower = self.request.user

        try :
            obj = self.get_queryset().get(
                follower = follower ,
                following = user_to_unfollow
            )
        except Follow.DoesNotExist:
            raise Http404('You are not following this user.')

        self.check_object_permissions(self.request , obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.following.username
        self.perform_destroy(instance)
        return Response({'detail': f'You are no longer following {username}'} , status = status.HTTP_200_OK)


class UserFollowersView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        followers = User.objects.filter(following__following=user)
        return followers

class UserFollowingView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        following = User.objects.filter(followers__follower=user)
        return following
