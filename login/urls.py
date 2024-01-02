from django.contrib import admin
from django.urls import path
from .views import loginview
urlpatterns = [
    path('',loginview.as_view()),
]