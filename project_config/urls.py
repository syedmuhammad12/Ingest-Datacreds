from django.contrib import admin
from django.urls import path
from .views import EmailView,SharepointView
urlpatterns = [
    path('email/',EmailView.as_view()),
    path('sharepoint/',SharepointView.as_view())
   ]