from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
# Create your models here.
class Email(models.Model):
    id = models.AutoField(primary_key=True)
    Tenant_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    email_id = models.EmailField(_('email_address'), unique=True, max_length = 200)
    
    required_fields = ['Tenant_id','client_secret','client_id','email_id']
    class Meta:
        db_table = 'email_config'
        

class Sharepoint(models.Model):
    id = models.AutoField(primary_key=True)
    Tenant_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100)
    host_name = models.CharField(max_length=50)
    site_name = models.CharField(max_length=50)

    required_fields = ['Tenant_id','client_secret','client_id','host_name','site_name']
    
    class Meta:
        db_table = 'sharepoint_config'