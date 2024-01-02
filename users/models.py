from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_id=models.CharField(unique=True, max_length = 20,null=True, blank=True)
    user_name=models.CharField( max_length = 20,null=True, blank=True)
    email = models.EmailField(_('email_address'), unique=True, max_length = 200)
    role= models.CharField(max_length=20)
    company_id = models.CharField(max_length=30,null=True)
    status = models.BooleanField(default=True)
    password = models.CharField(max_length=20, default='password123')
    required_fields = ['user_id','user_name','email', 'role', 'company_id']
    objects = models.Manager()

    def __str__(self):
        return "{}:{}..".format(self.id, self.email)




