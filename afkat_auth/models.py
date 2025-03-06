from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from phonenumber_field.modelfields import PhoneNumberField



# Create your models here.
class AfkatUserManger(UserManager):
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
    username = models.CharField(_("Username") ,blank = True,unique = True, max_length=150,)
    phone = PhoneNumberField(_("Phone Number"), blank=True,region =  None)
    country = CountryField(blank_label = ("Select Country"), blank=True)
    ROLE_CHOICES = (
        ("admin",_("Administrator")),
        ("user",_("User")),
        ("developer",_("Developer")),
        ("designer",_("Designer")),
    )
    role = models.CharField(_("Role"), choices = ROLE_CHOICES, default = 'user')
    first_name = None
    last_name = None
    profile_image = models.ImageField(upload_to="profile_pics/", blank = True, null = True )
    email = models.EmailField(_("email address"), unique=True)
    objects = AfkatUserManger()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    @property
    def is_developer(self):
        return self.role == "developer"
    @property
    def is_designer(self):
        return self.role == "designer"
    @property
    def is_admin(self):
        return self.role == "admin"
