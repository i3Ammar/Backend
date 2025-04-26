from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from django_countries.serializer_fields import  CountryField
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class AfkatUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff = True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser = True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(_("Username")  ,unique = True, max_length=150,)
    email = models.EmailField(_("email address"), unique=True)

    ROLE_CHOICES = (
        ("admin",_("Administrator")),
        ("user",_("User")),
        ("developer",_("Developer")),
        ("designer",_("Designer")),
    )
    role = models.CharField(_("Role"), choices = ROLE_CHOICES, default = 'user')
    objects = AfkatUserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = [ "username" ]

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userProfile')
    phone = PhoneNumberField(_("Phone Number"), blank=True,null =  True, region=None)
    country = CountryField(blank=True, null=True, blank_label="Select Country")
    profile_image = models.ImageField(default = "default_images/default_profile.jpg",upload_to="profile_pics/", blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

class Follow(models.Model):
    follower = models.ForeignKey(User , related_name = 'following',  on_delete = models.CASCADE )
    following = models.ForeignKey(User , related_name = "followers" , on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta :
        unique_together = ['follower','following']




def create_or_update_user_profile(sender, instance, created, **kwargs):
        if  created:
            Profile.objects.create(user=instance)
        else:
            if hasattr(instance, 'userProfile'):
                instance.userProfile.save()
            else:
                instance.delete()
post_save.connect(create_or_update_user_profile , sender = User)