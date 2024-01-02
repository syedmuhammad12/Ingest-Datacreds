from django.shortcuts import render
from .models import Company
from .serializers import  companyserializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authorization.views import VerifyTenant


class CompanyView(APIView):
    
    def post(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        company_number=request.data.get('company_number')
        company_name=request.data.get('company_name')
        company_abrrev=request.data.get('company_abbrev')
        company=Company.objects.using(tenant).create(company_number=company_number,company_name=company_name,company_abrrev=company_abrrev)
        company.save(using=tenant)
        return Response({"response": '  Company created succesfully'},status=status.HTTP_201_CREATED)
    
    def get(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        company=Company.objects.using(tenant).all()
        serializer = companyserializer(company, many=True)
        data = serializer.data
        status=200
        return Response(data,status)
    
    def put(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        company_id=request.data.get('company_id')
        company=Company.objects.using(tenant).get(company_id=company_id)
        data=request.data
        serializer=companyserializer(company,data=data,partial=True)
        if serializer.is_valid():
            serializer.save(using=tenant)
            return Response({'status':'updated','data':serializer.data})
        else:
            return Response({'status':' not updated'})
    

class companyeditview(APIView):

    def get(self, request,company_id):
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            company=Company.objects.using(tenant).filter(company_id=company_id)
            serializer = companyserializer(company, many=True)
            data = serializer.data
            return Response(data)
    
    
    def delete(self, request,company_id):
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            company=Company.objects.using(tenant).filter(company_id=company_id)
            company.delete(using=tenant)
            return Response({"response":"company deleted"})
