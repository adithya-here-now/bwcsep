from django import forms
from .models import UploadedPDF
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedPDF
        fields = ['pdf_file']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
