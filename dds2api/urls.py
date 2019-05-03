from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('tenant/', views.TenantList.as_view()),
    path('tenant/<int:pk>/', views.TenantDetail.as_view()),
    path('tag/', views.TagList.as_view()),
    path('tag/<int:pk>/', views.TagDetail.as_view()),
    # jwt endpoints
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
