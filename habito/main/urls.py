from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('create', views.create_habit, name='create_habit'),
    path('dashboard', views.dashboard, name='dashboard'),
]