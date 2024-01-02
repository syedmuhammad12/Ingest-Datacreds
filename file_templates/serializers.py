from rest_framework import serializers
from .models import FileTemplatesModel

class FileTemplatesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTemplatesModel
        fields = ['template_id', 'template_name', 'file_type']


class FileTemplatesEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTemplatesModel
        fields = ['template_id', 'template_name', 'file_type']
