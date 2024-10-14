# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.extractor_view, name='extractor_view'),
    path('start-extraction/', views.extractor_view, name='start_extraction'),
    path('get-progress/', views.get_progress, name='get_progress'),
]