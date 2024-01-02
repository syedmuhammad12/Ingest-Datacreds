from django.contrib import admin
from django.urls import path
from .views import userview,usereditview

urlpatterns = [
    # path('login/', LoginAPI.as_view(), name='login'),
    path('', userview.as_view()),
    path('adduser/', userview.as_view()),
    path('edituser/',userview.as_view()),
    path('edit/<id>', usereditview.as_view()),
    path('delete/<id>',usereditview.as_view())
   ]