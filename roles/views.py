from django.shortcuts import render
from .models import Roles, Modules, RoleHasModules
from .serialaizers import rolesserializer, ModulesSerializer, RoleHasModulesSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime
from authorization.views import VerifyTenant


# Create your views here.


class RolesView(APIView):

    def post(self, request):
        role_name = request.data.get('role_name')
        role_desc = request.data.get('role_desc')
        module = request.data.get('module')
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        role = Roles(role_name=role_name, role_description=role_desc, created_at=created_at,
                     updated_at=updated_at)
        role.save(using=tenant)
        role_id = Roles.objects.using(tenant).latest('id')
        for val in module:
            module_id = Modules.objects.using(tenant).get(IdModuleAccess=val['value'])
            role_has_modules = RoleHasModules(IdModuleAccess=module_id, IdRole=role_id)
            role_has_modules.save(using=tenant)

        return Response({'status': 'created succesfully'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            roles = Roles.objects.using(tenant).filter(id__gt=1)
            serializer = rolesserializer(roles, many=True)
            data = serializer.data
            return Response(data)
        except Exception as e:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


    def put(self, request):

        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        id = request.data.get('id')
        role = Roles.objects.using(tenant).get(id=id)
        # print(request.data)
        # exit(1)
        data = request.data
        data['updated_at'] = datetime.datetime.now()
        serializer = rolesserializer(role, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(using=tenant)
            module = request.data.get('module')
            if type(module) == list:
                module_delete = RoleHasModules.objects.using(tenant).filter(IdRole=role)
                module_delete.delete()
                for val in module:
                    module_id = Modules.objects.using(tenant).get(IdModuleAccess=val['value'])
                    role_has_modules = RoleHasModules(IdModuleAccess=module_id, IdRole=role)
                    role_has_modules.save(using=tenant)
            return Response({'status': 'updated', 'data': serializer.data})
        else:
            return Response({'status': ' not updated'})


class roleseditview(APIView):

    def get(self, request, id):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        role = Roles.objects.using(tenant).filter(id=id)
        serializer = rolesserializer(role, many=True)
        data = serializer.data

        role_has_modules = RoleHasModules.objects.using(tenant).filter(IdRole=id)
        module_data = RoleHasModulesSerializer(role_has_modules, many=True).data
        return Response({"role": data, "modules": module_data})

    def delete(self, request, id):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        role = Roles.objects.using(tenant).get(id=id)
        module_delete = RoleHasModules.objects.using(tenant).filter(IdRole=role)
        module_delete.delete()
        role.delete()
        return Response({"response": "Role deleted"})


class ModuleView(APIView):

    def get(self, request):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        modules = Modules.objects.using(tenant).all().exclude(ModuleName__in=['roles', 'file template'])
        serializer = ModulesSerializer(modules, many=True)
        data = serializer.data
        return Response(data)
