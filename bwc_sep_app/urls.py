from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # Default route is login
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('welcome/', views.dashboard, name='welcome'),  # If "dashboard" is your landing page
    path('upload/', views.dashboard, name='upload_pdf'),  # You already handle upload in dashboard
    path('list/', views.dashboard, name='pdf_list'),  # Same view — adjust if needed
]
