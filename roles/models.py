from django.db import models
import datetime


# Create your models here.
class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=90,blank=False,unique=True,null=False)
    role_description = models.CharField(max_length=200,blank=False,null=False)
    created_at = models.DateTimeField(default=datetime.datetime.now(), null=True)
    updated_at = models.DateTimeField(default=datetime.datetime.now(), null=True)
    required_fields = ['role_name','role_description']

    class Meta:
        """Roles Table"""
        db_table = 'Roles'

class Modules(models.Model):
    """Modules model"""
    IdModuleAccess = models.AutoField(db_column="idmodule_access", primary_key=True)
    ModuleName = models.CharField(db_column="module_name", max_length=45)

    class Meta:
        """Meta data"""
        db_table = "modules"

class RoleHasModules(models.Model):
    """Roles Has Modules model"""
    IdRoleHasModuleAccess = models.AutoField(db_column="idrole_has_module_access",
                                             primary_key=True)
    IdRole = models.ForeignKey(Roles, on_delete=models.DO_NOTHING,
                               db_column="id_role", blank=True, null=True)
    IdModuleAccess = models.ForeignKey(Modules, on_delete=models.DO_NOTHING,
                                       db_column="idmodule_access", blank=True, null=True)

    class Meta:
        """Meta data"""
        db_table = "role_has_modules"
