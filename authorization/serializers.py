"""Serializers for authorization app"""
# pylint: disable=too-few-public-methods
# pylint: disable=no-member
from rest_framework import serializers
from .models import Config


class ConfigSerializer(serializers.ModelSerializer):
    """Config serializer"""

    class Meta:
        """meta validated_data"""
        model = Config
        fields = "__all__"

class CurrentRolePermissionSerializer(serializers.Serializer):
    """Current role Permission serializer, define fields here."""
    
    permission_id = serializers.IntegerField()
    action = serializers.CharField()
    module = serializers.CharField()