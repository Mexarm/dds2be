""" dds2api models"""

import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError


KEY_LENGTH = 15


class AuthSignature(models.Model):
    """Abstract class with fields, to keep track of the user's
       and datetime of creation or modification """

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created",
        null=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_modified",
        null=True
    )

    class Meta:
        abstract = True


class TenantAware(models.Model):
    """Abstract class that defines a tenant on models"""

    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)

    class Meta:
        abstract = True

# MODELS


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    mobile_number = models.CharField(max_length=20)
    verified_number = models.BooleanField()
    enable_2fa = models.BooleanField()
    tenant = models.ManyToManyField('Tenant')
    roles = models.ManyToManyField('Role', blank=True)

    def __str__(self):
        return self.user.username


class Tenant(AuthSignature):
    """Tenant"""

    tenant = models.CharField(
        max_length=128, unique=True, blank=False)
    description = models.CharField(max_length=256, blank=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.tenant


class Role(TenantAware, AuthSignature):
    ADMIN = 'admin'
    TEMPLATE_EDITOR = 'template_editor'
    ROLES = (
        (ADMIN, 'Administrator'),
        (TEMPLATE_EDITOR, 'Template Editor')
    )
    role = models.CharField(max_length=KEY_LENGTH, choices=ROLES)

    class Meta:
        unique_together = ('role', 'tenant')


class BalanceEntry(TenantAware, AuthSignature):
    """Balance Entry"""

    CHANNEL_EMAIL = 'EMAIL'
    CHANNEL_SMS = 'SMS'
    PAYMENT = 'PAYMENT'
    CHANNEL_TYPES = (
        (CHANNEL_EMAIL, 'e-mail'),
        (CHANNEL_SMS, 'text message (sms)')
    )
    ORIGIN_TYPE = (
        (PAYMENT, 'confirmed payment'),
    )

    channel_type = models.CharField(
        choices=CHANNEL_TYPES,
        max_length=KEY_LENGTH,
        verbose_name='type of channel'
    )
    qty = models.FloatField(null=False, blank=False)
    balance = models.FloatField(null=False, blank=False)
    origin_type = models.CharField(
        choices=ORIGIN_TYPE,
        max_length=KEY_LENGTH)
    origin_id = models.CharField(max_length=40)

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return f'{self.origin_type}  {self.channel_type} ${self.qty}'


class Tag(TenantAware, AuthSignature):
    """Tag"""

    tag = models.CharField(max_length=32, null=False, blank=False)
    slug = models.SlugField(max_length=32, null=False,
                            blank=False, editable=False,
                            validators=[])

    class Meta:
        ordering = ('slug',)
        unique_together = ('slug', 'tenant')

    def __str__(self):
        return self.tag

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if (
                exclude and
                'slug' in exclude and
                Tag.objects.filter(
                    tenant=self.tenant,
                    slug=slugify(self.tag)
                ).exists()
        ):
            raise ValidationError(
                'Tag already exists'
            )

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        self.slug = slugify(self.tag)
        super(Tag, self).save(*args, **kwargs)


class StorageCredential(TenantAware, AuthSignature):
    """
    Storage Credentials
    """

    AWS_S3 = 'AWS_S3'
    BASIC_AUTH_URL = 'BASIC_AUTH_URL'
    STORAGE_TYPES = (
        (AWS_S3, 'AWS S3'),
        (BASIC_AUTH_URL, 'URL WITH BASIC AUTH')
    )
    name = models.CharField(max_length=40, null=False,
                            blank=False, unique=True)
    stype = models.CharField(max_length=KEY_LENGTH, choices=STORAGE_TYPES)
    access_key_id = models.CharField(max_length=32)
    secret_access_key = models.CharField(max_length=32)


class Sender(TenantAware, AuthSignature):
    """
    Sender
    """

    name = models.CharField(max_length=128)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    email_verified = models.BooleanField(default=False, editable=False)
    mobile_verified = models.BooleanField(default=False, editable=False)
    vefification_key = models.CharField(
        max_length=36, default=uuid.uuid4, editable=False)

    def _get_formatted_email(self):
        """return the formated email in the form
           Name <myemail@example.com>"""
        return f'{self.name} <{self.email}>'

    formatted_email = property(_get_formatted_email)

    def __str__(self):
        return f'{self.formatted_email} / ({self.mobile_number})'


class Attachment(TenantAware, AuthSignature):
    """
    email attachment
    """
    description = models.CharField(
        max_length=80, unique=True, null=False, blank=False)
    file = models.FileField(upload_to='uploads/')
