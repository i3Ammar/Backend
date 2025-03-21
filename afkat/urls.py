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
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

import afkat_home.views


schema_view = get_schema_view(
    openapi.Info(
        title = "My Api",
        default_version='v1',
        description = "My description",
        terms_of_service = "https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="<EMAIL>"),
        license=openapi.License(name="MIT License"),
        url = 'http://127.0.0.1:8000/api/'
    ),
    public=True,
    permission_classes = [ permissions.AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',afkat_home.views.index , name = "home"),
    path ('api/auth/', include ('afkat_auth.urls')),
    path('api/home/',include('afkat_home.api.urls'))


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
    path("swagger/",schema_view.with_ui('swagger', cache_timeout = 0 ), name = 'schema-swagger-ui'),
    path('__debug__/', include(debug_toolbar.urls)),
    path("__reload__/", include("django_browser_reload.urls")),
    ]