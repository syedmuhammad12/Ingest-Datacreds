from django.urls import path
from file_templates import views

urlpatterns = [
    path('create/', views.FileTemplates.as_view()),
    path('list/', views.FileTemplates.as_view()),
    path('edit/<int:id>', views.EditTemplate.as_view()),
    path('update/<int:id>', views.EditTemplate.as_view()),
    path('dashboard', views.Dashboard.as_view())
]

