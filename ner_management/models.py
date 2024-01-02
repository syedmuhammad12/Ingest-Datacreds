import os
from django.utils.translation import gettext_lazy as _
from django.db import models


def get_upload_file_path(self, filename):
    """
    Get the file path of S3 bucket
    """
    return os.path.join('data/train/', filename)

class NERTrainingFiles(models.Model):

    class ArchivedStatus(models.IntegerChoices):
        NO = 0, _('No')
        YES = 1, _('Yes')

    file_id = models.AutoField(primary_key=True)
    file_name = models.FileField(blank=False, null=True, max_length=500, upload_to=get_upload_file_path)
    original_file_name = models.CharField(blank=False, null=True, max_length=500)
    file_uploaded_type = models.CharField(blank=False, null=True, max_length=500)
    file_format = models.CharField(blank=False, null=True,max_length=500)
    file_size = models.CharField(blank=False, null=True, max_length=50)
    is_archived = models.IntegerField(choices=ArchivedStatus.choices,
                                       default=ArchivedStatus.NO)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data"""
        db_table = 'ner_training_files'

class TrainingStatus (models.Model):
    ts_id = models.AutoField(primary_key=True)
    training_status = models.BooleanField(default=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data"""
        db_table = 'ner_training_status'
