from django.urls import include, path

from afkat_auth.views import UserDetail, FollowUserView, UnfollowUserView, UserFollowersView, UserFollowingView

urlpatterns = [
    path("rest_auth/", include("rest_framework.urls")),
    path("", include("dj_rest_auth.urls")),
    path("register/", include("dj_rest_auth.registration.urls")),
    path("users/<int:pk>", UserDetail.as_view(), name="api_user_detail"),
    path('follow/<int:pk>/', FollowUserView.as_view() , name = 'follow_user'),
    path('unfollow/<int:pk>/', UnfollowUserView.as_view() , name = 'unfollow_user'),
    path('users/<int:pk>/followers/', UserFollowersView.as_view(), name='user_followers'),
    path('users/<int:pk>/following/', UserFollowingView.as_view(), name='user_following'),
]
