from rest_framework import serializers
from .models import Company
from rest_framework.serializers import ModelSerializer


class companyserializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields='__all__'