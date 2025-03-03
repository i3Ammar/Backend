from django.urls import include, path
from django_registration.backends.activation.views import RegistrationView
from .forms import UserRegistrationForm
from .views import  profile



urlpatterns = [
path ('accounts/', include ('django_registration.backends.one_step.urls')) ,
path('accounts/', include ('django.contrib.auth.urls')) ,
path ('accounts/profile/',profile , name = 'profile') ,
path(
    "accounts/register/",
    RegistrationView.as_view(form_class=UserRegistrationForm),
    name="django_registration_register",
),
]