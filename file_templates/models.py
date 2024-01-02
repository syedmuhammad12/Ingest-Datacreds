from django.db import models

# Create your models here.

class FileTemplatesModel(models.Model):
    template_id = models.AutoField(primary_key=True)
    template_name = models.CharField(null=True, blank=True, max_length=50)
    file_type = models.CharField(null=True, blank=True, max_length=50)

    class Meta:
        db_table = 'file_templates'
