from django.contrib import admin
from django.urls import path
from R2xml import views
urlpatterns = [
    path('',views.R2xml.as_view()),
    path('linelist',views.R2xmlLineList.as_view())
   ]