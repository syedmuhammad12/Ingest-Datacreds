"""Serializers for file management models"""
from rest_framework import serializers
from .models import NERTrainingFiles

class NERTrainingFilesSerializer(serializers.ModelSerializer):
    """Training file serializer"""
    class Meta:
        """Meta data"""
        model = NERTrainingFiles
        fields = ['original_file_name', 'file_name']


class NERTrainingFilesListSerializer(serializers.ModelSerializer):
    created_date_time = serializers.CharField()
    class Meta:
        model = NERTrainingFiles
        fields = ['file_id', 'original_file_name', 'file_format', 'file_size', 'file_uploaded_type',
                  'is_archived', 'created_datetime', 'updated_datetime', 'created_date_time']
