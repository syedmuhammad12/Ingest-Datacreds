from django.urls import path
from . import views

urlpatterns = [
    path('extract/', views.ReadFile.as_view(), name="extract_ner"),
    path('train/', views.TrainCreateModel.as_view(), name="train_ner"),
    path('train/files/<int:perPage>/<int:page>/', views.TrainingFiles.as_view(), name="training_files"),
    path('train/file/<int:file_id>', views.ViewTrainingFile.as_view(), name="view_train_file"),
    path('train/save_files/', views.SaveTrainingFiles.as_view(), name="training_files"),
    path('test/', views.TestModel.as_view(), name="test_ner"),
]