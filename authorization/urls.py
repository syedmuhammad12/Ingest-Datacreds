from django.urls import path
from authorization import views

urlpatterns = [
    path('email/', views.EmailConfig.as_view())
]