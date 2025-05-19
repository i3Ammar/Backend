from django.dispatch import receiver
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete

from afkat_auth.models import Profile, User, Follow

