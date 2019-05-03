"""dds2app forms"""

from django import forms
from .models import (
    StorageCredential,
    Attachment
)


class StorageCredentialForm(forms.ModelForm):
    """Storage Credentials"""
    access_key_id = forms.CharField(widget=forms.PasswordInput)
    secret_access_key = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = StorageCredential
        fields = '__all__'


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = '__all__'
