from django.contrib import admin
from django.urls import path
from .views import RolesView,roleseditview,ModuleView


urlpatterns = [
    path('',RolesView.as_view()),
    path('addrole/',RolesView.as_view()),
    path('rolesedit/',RolesView.as_view()),
    path('rolesedit/<id>', roleseditview.as_view()),
    path('rolesdelete/<id>',roleseditview.as_view()),
    path('moduleslist',ModuleView.as_view()),
   ]