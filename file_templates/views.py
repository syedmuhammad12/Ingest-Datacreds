from django.shortcuts import render
import logging
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from file_templates.models import FileTemplatesModel
from file_templates.serializers import FileTemplatesListSerializer, FileTemplatesEditSerializer

from authorization.views import VerifyTenant


# Create your views here.

class FileTemplates(APIView):
    def get(self, request):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            file_template = FileTemplatesModel.objects.using(tenant).all()
            file_template_data = FileTemplatesListSerializer(file_template, many=True).data
            response_data = {
                "data": file_template_data,
                'status': 200,
                'error': '0'
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)


    def post(self, request, *args, **kwargs):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            template_name = request.data['template_name']
            file_type = request.data['file_type']

            file_template = FileTemplatesModel(template_name=template_name)
            file_template.file_type = file_type
            file_template.save(using=tenant)

            response_data = {
                'message': 'File Template created successfully',
                'error': "0",
                'status_code': 200
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)


class EditTemplate(APIView):
    def get(self, request, id):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            m_data = FileTemplatesModel.objects.using(tenant).get(template_id=id)
            file_template_data = FileTemplatesEditSerializer(m_data).data

            response_data = {
                'data': file_template_data,
                'error': '0',
                'status_code': 200
            }
            return Response(response_data, status=200)
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)

    def post(self, request, id):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            template = FileTemplatesModel.objects.using(tenant).get(template_id=id)
            template.template_name = request.data['template_name']
            template.file_type = request.data['file_type']
            template.save(using=tenant)

            response_data = {
                'message': 'File template updates successfully',
                'error': '0',
                'status_code': 200
            }
            return Response(response_data, status=200)
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)


class Dashboard(APIView):
    def get(self, request):
        try:
            tenant = VerifyTenant('test_data_ingestion').GetTenant()
            file_template = FileTemplatesModel.objects.using(tenant).all()
            file_template_data = FileTemplatesListSerializer(file_template, many=True).data
            response_data = {
                "data": file_template_data,
                'status': 200,
                'error': '0'
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)