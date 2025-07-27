from django.contrib import admin
from .models import UploadedPDF  # ✅ Only import what exists

admin.site.register(UploadedPDF)
