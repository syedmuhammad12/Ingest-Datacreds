from django.shortcuts import render
from users import models, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authorization.views import VerifyTenant

from roles.models import RoleHasModules, Roles
from roles.serialaizers import RoleHasModulesSerializer


# Create your views here.
class loginview(APIView):
    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")
        print(request.META['HTTP_TENANT_CODE'])
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        print(models.User.objects.using(tenant).values_list())
        user = models.User.objects.using(tenant).filter(email=username, password=password, role=role)
        # print(user)
        # print(vars(user))
        # print(request.data)
        # exit(1)
        print(user)
        if user:
            print("herereee")
            result = serializers.userserializer(user, many=True).data[0]
            if int(role) == 1:
                result['modules'] = ["all"]
                result['role_name'] = 'super admin'
            else:
                role_has_modules = RoleHasModules.objects.using(tenant).filter(IdRole=role)
                module_data = RoleHasModulesSerializer(role_has_modules, many=True).data
                temp = []
                for val in module_data:
                    temp.append(val['IdModuleAccess']['ModuleName'])
                result['modules'] = temp
                role_data = Roles.objects.using(tenant).get(id=role)
                result['role_name'] = role_data.role_name
            result['tenant'] = request.META['HTTP_TENANT_CODE']
            return Response({"result": "success", 'data': result}, status=status.HTTP_200_OK)
        else:
            return Response({'status': "login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
