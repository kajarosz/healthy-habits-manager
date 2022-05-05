from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user/<int:pk>/habit/create', views.create_habit, name='create_habit'),
]