from django.urls import path
from r2import import views

urlpatterns = [
    path("import", views.r2import.as_view())
]