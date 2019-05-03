from django.utils.text import slugify
from rest_framework import serializers
from .models import (
    Tenant,
    Tag
)


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('id', 'tenant', 'description')


class TagSerializer(serializers.ModelSerializer):
    # pylint: disable=W0221
    def validate(self, data):
        """
        Check if the slug for the tag exists
        """
        print(data)
        if Tag.objects.filter(tenant=data['tenant'], slug=slugify(data['tag'])).exists():
            raise serializers.ValidationError("tag already exists")
        return data
    # https://www.django-rest-framework.org/api-guide/relations/#nested-relationships
    tenant = TenantSerializer(many=False, read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'tenant', 'tag', 'slug')
