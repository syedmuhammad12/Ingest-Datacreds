"""Serializers for file management models"""
from rest_framework import serializers
from .models import File
from file_templates.models import FileTemplatesModel

class CreateFileSerializer(serializers.ModelSerializer):
    """Create file serializer"""
    class Meta:
        """Meta data"""
        model = File
        fields = ['id_file', 'original_file_name', 'file_template_id', 'file_format', 'file_size',
                  'is_delete', 'created_datetime', 'updated_datetime', 'file_type']


class FileTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTemplatesModel
        fields = ['template_name']


class FileListSerializer(serializers.ModelSerializer):
    # file_template = FileTemplatesSerializer(many=True, read_only=True)
    class Meta:
        model = File
        fields = "__all__"
        depth = 1
