from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CustomLoginView  , ProfileViewSet



router = DefaultRouter()
router.register(r'profile' , ProfileViewSet , basename='profile')
urlpatterns = [


    path('', include("rest_framework.urls")),
    path('profile/', ProfileViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile'),
    path('dra/', include('dj_rest_auth.urls')),
    path('dra/reg/', include('dj_rest_auth.registration.urls')),

    # path('accounts/', include ('django.contrib.auth.urls')) ,
    # path('login/', CustomLoginView.as_view(), name='custom_login'),
    # # path('logout/',LogoutView.as_view(), name='logout'),
    # path('register/', CustomRegistrationView.as_view(), name='custom_register'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)) ,
]
