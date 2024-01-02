from django.shortcuts import render
from .models import Email,Sharepoint
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
class EmailView(APIView):
    def post(self,request):
        Tenant_id=request.data.get('Tenant_id')
        Client_secret=request.data.get('Client_secret')
        Client_id=request.data.get('Client_id')
        email=request.data.get('Email')
        email=Email.objects.create(Tenant_id=Tenant_id,client_id=Client_id,client_secret=Client_secret,email_id=email)
        email.save()
        return Response({'status':'created succesfully'},status=status.HTTP_201_CREATED)

class SharepointView(APIView):
    def post(self,request):
        Tenant_id=request.data.get('Tenant_ID')
        Client_secret=request.data.get('Client_secret')
        Client_id=request.data.get('Client_id')
        host_name=request.data.get('host_name')
        site_name=request.data.get('site_name')
        sharepoint=Sharepoint.objects.create(Tenant_id=Tenant_id,client_id=Client_id,client_secret=Client_secret,host_name=host_name,site_name=site_name)
        sharepoint.save()
        return Response({'status':'created succesfully'},status=status.HTTP_201_CREATED)
