from django.shortcuts import render
from .models import User
from .serializers import userserializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random, string
from authorization.views import VerifyTenant


# Create your views here.
class userview(APIView):
    def get(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        user = User.objects.using(tenant).all().exclude(role='1')
        serializer = userserializer(user, many=True)
        data = serializer.data
        for i in range(len(data)):
            # print(data[i]['status'])
            if data[i]['status'] == True:
                data[i]['status'] = 'Active'
            else:
                data[i]['status'] = 'Inactive'
        return Response(data)

    def post(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        user_id = request.data.get('user_id')
        user_name = request.data.get('user_name')
        email = request.data.get('email')
        role = request.data.get('role')
        company_id = request.data.get('company_id', None)
        user_status = request.data.get('status')
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user = User.objects.using(tenant).create(user_id=user_id, user_name=user_name, email=email, role=role,
                                                 company_id=company_id, status=user_status, password=password)
        user.save(using=tenant)
        return Response({'status': 'created succesfully'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        id = request.data.get('id')
        user = User.objects.using(tenant).get(id=id)
        serializer = userserializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(using=tenant)
            return Response({'status': 'updated', 'data': serializer.data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'status': ' not updated'})


class usereditview(APIView):
    def get(self, request, id):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        user = User.objects.using(tenant).filter(id=id)
        serializer = userserializer(user, many=True)
        data = serializer.data
        for i in range(len(data)):
            if data[i]['status'] == True:
                data[i]['status'] = 'Active'
            else:
                data[i]['status'] = 'Inactive'
        return Response(data)

    def delete(self, request, id):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        user = User.objects.using(tenant).filter(id=id)
        user.delete(using=tenant)
        return Response({"response": "user deleted"})
