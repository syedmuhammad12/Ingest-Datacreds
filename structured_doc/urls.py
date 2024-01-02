from django.urls import path
from . import views


urlpatterns = [
    path("create_training_file/", views.ExtractTrainData.as_view()),
]