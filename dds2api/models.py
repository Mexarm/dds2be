""" dds2api models"""

import uuid
import base64

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField

from dds2be.storage_backends import PrivateMediaStorage

KEY_LENGTH = 20


class AuthSignature(models.Model):
    """Abstract class with fields, to keep track of the user's
       and datetime of creation or modification """

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="%(app_label)s_%(class)s_created",
                                   null=True
                                   )
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    related_name="%(app_label)s_%(class)s_modified",
                                    null=True
                                    )

    class Meta:
        abstract = True


class TenantAware(models.Model):
    """Abstract class that defines a tenant on models"""

    tenant = models.ForeignKey('Tenant',
                               on_delete=models.CASCADE)

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
    roles = models.ManyToManyField('Role',
                                   blank=True)

    def __str__(self):
        return self.user.username


class Tenant(AuthSignature):
    """Tenant"""

    tenant = models.CharField(max_length=128,
                              unique=True,
                              blank=False)
    description = models.CharField(max_length=256,
                                   blank=True)

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
    role = models.CharField(max_length=KEY_LENGTH,
                            choices=ROLES)

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

    channel_type = models.CharField(choices=CHANNEL_TYPES,
                                    max_length=KEY_LENGTH,
                                    verbose_name='type of channel')
    qty = models.FloatField(null=False,
                            blank=False)
    balance = models.FloatField(null=False,
                                blank=False)
    origin_type = models.CharField(choices=ORIGIN_TYPE,
                                   max_length=KEY_LENGTH)
    origin_id = models.CharField(max_length=40)

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return f'{self.origin_type}  {self.channel_type} ${self.qty}'


class Tag(TenantAware, AuthSignature):
    """Tag"""

    tag = models.CharField(max_length=32,
                           null=False,
                           blank=False)
    slug = models.SlugField(max_length=32,
                            null=False,
                            blank=False,
                            editable=False,
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
    name = models.CharField(max_length=40,
                            null=False,
                            blank=False,
                            unique=True)
    stype = models.CharField(max_length=KEY_LENGTH,
                             choices=STORAGE_TYPES)
    access_key_id = models.CharField(max_length=32)
    secret_access_key = models.CharField(max_length=32)


class Domain(TenantAware, AuthSignature):
    """
    Domain
    """

    name = models.CharField(max_length=128)
    verified = models.BooleanField(default=False)


class Sender(TenantAware, AuthSignature):
    """
    Sender
    """

    name = models.CharField(max_length=128)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    email_verified = models.BooleanField(default=False,
                                         editable=False)
    mobile_verified = models.BooleanField(default=False,
                                          editable=False)
    vefification_key = models.UUIDField(default=uuid.uuid4,
                                        editable=False)

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
    ORIGIN_FROM_URL = 'URL'
    ORIGIN_FROM_S3_OBJECT_KEY = 'S3'
    ORIGINS = (
        (ORIGIN_FROM_URL, 'Retrieve attachment from a URL'),
        (ORIGIN_FROM_S3_OBJECT_KEY, 'Retrieve attachment from AWS S3 Object Key'),
    )

    ATTACHMENT_NAME_FROM_URL_PARAM = 'URL_PARAM'
    ATTACHMENT_NAME_FROM_URL_CONTENT_DISPOSITION = 'CONTENT_DISPOSITION'
    ATTACHMENT_NAME_SPECIFY = 'SPECIFIED'

    URL_ORIGING_NAMING_MODE = (
        (ATTACHMENT_NAME_FROM_URL_PARAM, 'extract name from URL param'),
        (ATTACHMENT_NAME_FROM_URL_CONTENT_DISPOSITION,
         'extract name from "Content-Disposition" header'),
        (ATTACHMENT_NAME_SPECIFY, 'specify attachment name')
    )

    description = models.CharField(max_length=80,
                                   unique=True,
                                   null=False,
                                   blank=False)
    file = models.FileField(upload_to='uploads/',
                            storage=PrivateMediaStorage(),
                            blank=True)
    field_name = models.CharField(max_length=80,
                                  blank=True)
    origin = models.CharField(max_length=KEY_LENGTH,
                              blank=True,
                              choices=ORIGINS)
    http_method = models.CharField(max_length=KEY_LENGTH,
                                   choices=(
                                       ('GET', 'GET'),
                                       ('POST', 'POST'),),
                                   blank=True)
    url_origing_naming_mode = models.CharField(max_length=KEY_LENGTH,
                                               choices=URL_ORIGING_NAMING_MODE,
                                               blank=True)
    url_json_params = JSONField(null=True,
                                help_text='example: { "account": "{{my_account_no}}" }',
                                blank=True)
    specify_name = models.CharField(max_length=256,
                                    help_text=(
                                        'directly specify the name of the attachment'
                                        'or use variables like {{myfield}}.pdf'
                                    ),
                                    blank=True
                                    )
    aws_s3_bucket_name = models.CharField(max_length=256,
                                          blank=True)
    aws_s3_object_key = models.CharField(max_length=256,
                                         blank=True)
    unzip = models.BooleanField(default=False,
                                help_text=(
                                    'if file is compressed (.zip), '
                                    'extract files and then attach')
                                )
    credentials = models.ForeignKey(StorageCredential,
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE)

    def _original_filename(self):
        encoded_filename = self.file.name.split('/')[-1]
        return base64.urlsafe_b64decode(encoded_filename).decode('utf-8')

    original_filename = property(_original_filename)

    def __str__(self):
        return f'{self.description} ({self.original_filename})'


class Broadcast(TenantAware, AuthSignature):
    EMAIL_CHANNEL = 'EMAIL'
    SMS_CHANNEL = 'SMS'
    CHANNEL_TYPES = (
        (EMAIL_CHANNEL, 'e-mail'),
        (SMS_CHANNEL, 'SMS text message'),
    )
    STATUS_DRAFT = 'DRAFT'

    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False)
    description = models.CharField(max_length=256)
    channel_type = models.CharField(max_length=KEY_LENGTH,
                                    choices=CHANNEL_TYPES)
    domain = models.ForeignKey(Domain,
                               null=True,
                               on_delete=models.CASCADE)
    sender = models.ForeignKey(Sender,
                               null=True,
                               on_delete=models.CASCADE),
    email_subject = models.CharField(max_length=256)
    status = models.CharField(max_length=KEY_LENGTH)
    tags = models.ManyToManyField(Tag)
    storage_credentials = models.ForeignKey(StorageCredential,
                                            on_delete=models.CASCADE)
    email_body = models.TextField()
    email_attachments = models.ManyToManyField(Attachment)


class DataSet(TenantAware, AuthSignature):
    ENCODING_ASCII = 'ascii'
    ENCODING_UTF8 = 'utf-8'
    ENCODING_ISO88591 = 'iso-8859-1'
    ENCODINGS = (
        (ENCODING_ASCII, ENCODING_ASCII),
        (ENCODING_UTF8, ENCODING_UTF8),
        (ENCODING_ISO88591, ENCODING_ISO88591)
    )
    original_filename = models.CharField(max_length=256)
    uploaded_file = models.FileField(upload_to='datasets/',
                                     storage=PrivateMediaStorage(),
                                     blank=True)
    description = models.CharField(max_length=256)
    system_tag = models.CharField(max_length=256)
    file_encoding = models.CharField(max_length=KEY_LENGTH,
                                     choices=ENCODINGS,
                                     default=ENCODING_UTF8)
    file_has_header = models.BooleanField(null=False,
                                          default=False)
    # https://github.com/gradam/django-better-admin-arrayfield
    file_fields = ArrayField(models.CharField(max_length=64, blank=True))
    file_delimiter = models.CharField(max_length=4,
                                      default=',')
    file_quotechar = models.CharField(max_length=1,
                                      default='"')
    status = models.CharField(max_length=KEY_LENGTH,
                              default='')
    # fieldmap?
