from rest_framework import serializers
from .models import  Roles,Modules,RoleHasModules


class rolesserializer(serializers.ModelSerializer):
    class Meta:
        model=Roles
        fields='__all__'

class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Modules
        fields='__all__'

class RoleHasModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model=RoleHasModules
        fields='__all__'
        depth=1