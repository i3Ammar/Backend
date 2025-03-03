"""
URL configuration for afkat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django_registration.backends.one_step.views import RegistrationView
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
import afkat_home.views

import debug_toolbar
import afkat_auth.views
from afkat_auth.forms import UserRegistrationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',afkat_home.views.index , name = "home"),
    path ('', include ('afkat_auth.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
    path("__reload__/", include("django_browser_reload.urls")),
    ]
