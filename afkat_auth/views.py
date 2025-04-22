from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status

from afkat_auth.models import User
from afkat_auth.serializers import UserProfileSerializer


# Create your views here.

@login_required
def profile(request):
    return render(request, "afkat_auth/profile.html")


class UserDetail(generics.RetrieveAPIView,):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


    @method_decorator(cache_page(5 * 60))
    def get(self, *args, **kwargs):
        return super(UserDetail, self).get(*args, **kwargs)
