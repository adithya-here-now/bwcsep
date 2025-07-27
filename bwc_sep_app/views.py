import os
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User

from .models import UploadedPDF
from .forms import PDFUploadForm, CustomUserCreationForm

from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('welcome')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def welcome(request):
    return render(request, 'welcome.html')


@login_required
def dashboard(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_instance = form.save(commit=False)
            pdf_instance.user = request.user
            pdf_instance.original_filename = request.FILES['pdf_file'].name
            pdf_instance.save()

            try:
                separate_pages(pdf_instance)
                return render(request, 'dashboard.html', {
                    'form': PDFUploadForm(),
                    'success': 'PDF processed successfully!',
                    'pdf': pdf_instance
                })
            except Exception as e:
                return render(request, 'dashboard.html', {
                    'form': form,
                    'error': f'Failed to process PDF: {e}'
                })
    else:
        form = PDFUploadForm()

    return render(request, 'dashboard.html', {'form': form})


# ✅ Color detection helper
def is_color(img, threshold=0.02):
    img = img.convert('RGB')
    np_img = np.array(img)
    r, g, b = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2]

    # Calculate how many pixels are not grayscale (r ≈ g ≈ b)
    diff_pixels = np.sum((r != g) | (g != b))
    total_pixels = np_img.shape[0] * np_img.shape[1]

    color_ratio = diff_pixels / total_pixels
    return color_ratio > threshold  # True if enough pixels are colored


# ✅ Separation logic
def separate_pages(pdf_instance):
    input_pdf_path = pdf_instance.pdf_file.path
    reader = PdfReader(input_pdf_path)
    bw_writer = PdfWriter()
    color_writer = PdfWriter()

    POPPLER_PATH = r"C:\poppler\poppler-24.08.0\Library\bin"  # ✅ Use your actual poppler path
    images = convert_from_path(input_pdf_path, poppler_path=POPPLER_PATH)

    for i, img in enumerate(images):
        if is_color(img):
            color_writer.add_page(reader.pages[i])
        else:
            bw_writer.add_page(reader.pages[i])

    # Output paths
    bw_dir = os.path.join(settings.MEDIA_ROOT, 'output', 'bw')
    color_dir = os.path.join(settings.MEDIA_ROOT, 'output', 'color')
    os.makedirs(bw_dir, exist_ok=True)
    os.makedirs(color_dir, exist_ok=True)

    bw_path = os.path.join(bw_dir, f'bw_{pdf_instance.id}.pdf')
    color_path = os.path.join(color_dir, f'color_{pdf_instance.id}.pdf')

    # Save PDFs
    with open(bw_path, 'wb') as f:
        bw_writer.write(f)
    with open(color_path, 'wb') as f:
        color_writer.write(f)

    # Save file paths to model
    pdf_instance.black_white_pages.name = f'output/bw/bw_{pdf_instance.id}.pdf'
    pdf_instance.color_pages.name = f'output/color/color_{pdf_instance.id}.pdf'
    pdf_instance.save()
