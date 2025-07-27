from django.db import models
from django.contrib.auth.models import User

class UploadedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_pdfs')
    pdf_file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255)
    black_white_pages = models.FileField(upload_to='output/bw/', blank=True, null=True)
    color_pages = models.FileField(upload_to='output/color/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_filename} uploaded by {self.user.username}"
