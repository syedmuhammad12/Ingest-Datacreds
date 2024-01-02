"""data_ingestion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', include('authorization.urls')),
    path('file/', include('file_management.urls')),
    path('config/', include('authorization.urls')),
    path('file-templates/', include('file_templates.urls')),
    path('ner/', include('ner_management.urls')),
    path('user/',include('users.urls')),
    path('roles/',include('roles.urls')),
    path('company/',include('company.urls')),
    path('settings/',include('project_config.urls')),
    path('login/',include('login.urls')),
    path('r2xml/',include('R2xml.urls')),
    path('structured/',include('structured_doc.urls'))
]
