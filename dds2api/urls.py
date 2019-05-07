from django.urls import path, include
# from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from . import views

router = DefaultRouter()  # pylint: disable=C0103
router.register(r'profile',
                views.ProfileViewSet,
                base_name='Profile')
router.register(r'tenant',
                views.TenantViewSet)
router.register(r'balance-entry',
                views.BalanceEntryViewSet,
                base_name='BalanceEntry')
router.register(r'tag',
                views.TagViewSet,
                base_name='Tag')
router.register(r'storage-credential',
                views.StorageCredentialViewSet,
                base_name='StorageCredential')
router.register(r'domain',
                views.DomainViewSet,
                base_name='Domain')
router.register(r'sender',
                views.SenderViewSet,
                base_name='Sender')
router.register(r'attachment',
                views.AttachmentViewSet,
                base_name='Attachment')
router.register(r'broadcast',
                views.BroadcastViewSet,
                base_name='Broadcast')
router.register(r'dataset',
                views.DataSetViewSet,
                base_name='DataSet')


urlpatterns = [
    # jwt endpoints
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    # api routes
    path('api/', include(router.urls)),


]
