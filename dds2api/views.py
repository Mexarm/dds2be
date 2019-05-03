from rest_framework import generics, permissions
from django.http import HttpResponse

from .models import (
    Tenant,
    Tag,
)
from .serializers import (
    TenantSerializer,
    TagSerializer,
)

from .permissions import UserIsTenantMember, user_tenants


def test(request):
    mytags = Tag.objects.filter(tenant__in=user_tenants(request))
    tags = [
        f'{tag.tenant}/{tag.tag}' for tag in mytags]

    return HttpResponse(f'hello {request.user.username} your tags {tags}')


class TenantList(generics.ListCreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = (permissions.IsAdminUser)


class TenantDetail(generics.RetrieveUpdateDestroyAPIView):  # pylint: disable=too-many-ancestors
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = (permissions.IsAdminUser)


class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, UserIsTenantMember)

    def get_queryset(self):
        return Tag.objects.filter(tenant__in=user_tenants(self.request))


class TagDetail(generics.RetrieveUpdateDestroyAPIView):  # pylint: disable=too-many-ancestors
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated, UserIsTenantMember)

    def get_queryset(self):
        return Tag.objects.filter(tenant__in=user_tenants(self.request))
