from django.urls import path
from . import views

urlpatterns = [
    path('converter/', views.Config.as_view(), name="converter")
]