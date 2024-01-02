from django.contrib import admin
from django.urls import path
from .views import CompanyView,companyeditview


urlpatterns = [
    path('',CompanyView.as_view()),
    path('addcompany/',CompanyView.as_view()),
    path('editcompany/',CompanyView.as_view()),
    path('editcompany/<company_id>',companyeditview.as_view()),
    path('deletecompany/<company_id>',companyeditview.as_view()),
   ]