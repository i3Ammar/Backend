from django.urls import include, path
from django_registration.backends.activation.views import RegistrationView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



from .forms import UserRegistrationForm
from .views import  profile

from .views import CustomLoginView , CustomRegistrationView



urlpatterns = [

    # path ('accounts/', include ('django_registration.backends.one_step.urls')) ,
    # path ('accounts/', include ('django_registration.backends.activation.urls')),
    path('accounts/', include ('django.contrib.auth.urls')) ,
    path ('accounts/profile/',profile , name = 'profile') ,
    # path("accounts/register/", RegistrationView.as_view(form_class=UserRegistrationForm), name="django_registration_register",),

    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('register/', CustomRegistrationView.as_view(), name='custom_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
