"""
Models for File Management
"""
import os
from django.db import models, migrations
from file_templates.models import FileTemplatesModel


# Create your models here.
def get_upload_file_path(self, filename):
    """
    Get the file path of S3 bucket
    """
    result=self.file_size.split('__')
    self.file_size=result[0]
    tenant=result[1]
    latest_file_id = File.objects.using(tenant).latest('id_file')
    return os.path.join('uploads/', tenant+'/'+str(latest_file_id.id_file + 1), filename)


def get_target_file_path(self, filename):
    """
    Get file path for edit
    """
    latest_file_id = File.objects.latest('id_file')
    return os.path.join('uploads/', str(latest_file_id.id_file) + '/1', filename)


class File(models.Model):
    """
    Define the model columns
    """
    present = 0
    notpresent = 1
    STATUS = ((present, '0'), (notpresent, '1'))
    id_file = models.AutoField(primary_key=True)
    file_name = models.FileField(blank=True, null=True, max_length=500,
                                 upload_to=get_upload_file_path)
    original_file_name = models.CharField(blank=False, null=True, max_length=500)
    file_type = models.CharField(blank=True, null=True, max_length=500)
    file_format = models.CharField(blank=True, null=True, max_length=500)
    file_size = models.CharField(blank=True, null=True, max_length=50)
    file_template_id = models.ForeignKey(FileTemplatesModel, on_delete=models.DO_NOTHING,
                                         db_column='file_template_id', related_name='file_template')
    is_data_extracted = models.CharField(blank=True, null=True, max_length=1, default=0)
    pdf_page_count = models.CharField(blank=True, null=True, max_length=3, default=1)
    is_delete = models.CharField(choices=STATUS, default=present, max_length=25)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data"""
        db_table = 'file_management'

    def __str__(self):
        """Return File name"""
        return self.file_name.name


class DuplicateFilesTrack(models.Model):
    duplicate_file_id = models.AutoField(primary_key=True)
    download_type = models.CharField(blank=True, null=True, max_length=30)
    file_id = models.CharField(blank=True, null=True, max_length=500)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta data"""
        db_table = 'duplicate_files_track'
