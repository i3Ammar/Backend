from django.dispatch import receiver
from django.core.cache import cache
from django.db.models.signals import post_save

from afkat_auth.models import Profile , User

@receiver(post_save , sender = User)
def invalidate_profile_cache(sender, instance , **kwargs) :
    user_id = instance.user.id
    cache.delete(f'views.decorators.cache.cache_page.user_detail_{user_id}')

@receiver(post_save , sender = Profile)
def invalidate_profile_cache(sender, instance , **kwargs) :
    user_id = instance.user.id
    cache.delete(f'views.decorators.cache.cache_page.user_detail_{user_id}')
