"""dds2app admin site classes"""

from django.contrib import admin
from .forms import (
    StorageCredentialForm,
)

from .models import (
    Tenant,
    Role,
    Profile,
    BalanceEntry,
    Tag,
    StorageCredential,
    Sender,
    Attachment,
)


class AdminAuthSignature(admin.ModelAdmin):
    """Abstract class that overrides save_model'
       and updates the model with the user that created or
       modified the model instance"""

    exclude = ('created_by', 'modified_by')

    def save_model(self, request, obj, form, change):
        if change:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    class Meta:
        abstract = True


class TenantAdmin(AdminAuthSignature):
    """ Tenant """
    list_display = ('tenant', 'description', 'created_by', 'modified_by')
    #prepopulated_fields = {'slug': ['title']}

    # def has_change_permission(self, request, obj=None):
    #     has_class_permission = super(
    #         EntryAdmin, self).has_change_permission(request, obj)
    #     if not has_class_permission:
    #         return False
    #     if obj is not None and not request.user.is_superuser and request.user.id != obj.author.id:
    #         return False
    #     return True

    # def queryset(self, request):
    #     if request.user.is_superuser:
    #         return Entry.objects.all()
    #     return Entry.objects.filter(author=request.user)


class AdminBalanceEntry(AdminAuthSignature):
    """Balance Entry"""

    list_display = ('channel_type', 'qty', 'created_on',
                    'created_by', 'modified_on', 'modified_by')


class AdminTag(AdminAuthSignature):
    """Tag"""

    list_display = ('tenant', 'tag')


class AdminStorageCredential(AdminAuthSignature):
    """Storage Credential """
    form = StorageCredentialForm


class AdminSender(AdminAuthSignature):
    """Sender"""
    list_display = ('name', 'email', 'mobile_number',
                    'mobile_verified', 'email_verified')


class AdminAttachment(AdminAuthSignature):
    """Attachment"""


admin.site.register(Tenant, TenantAdmin)
admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(BalanceEntry, AdminBalanceEntry)
admin.site.register(Tag, AdminTag)
admin.site.register(StorageCredential, AdminStorageCredential)
admin.site.register(Sender, AdminSender)
admin.site.register(Attachment, AdminAttachment)
