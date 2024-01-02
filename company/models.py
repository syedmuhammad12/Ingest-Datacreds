from django.db import models

# Create your models here.
class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_number=models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=90,blank=False,unique=True)
    company_abrrev = models.CharField(max_length=20,null=True)
    required_fields = ['company_number','company_name']

    class Meta:
        """Company Table"""
        db_table = 'Company'
