"""Modal for authorization app"""
# pylint: disable=too-few-public-methods
# pylint: disable=no-member
from django.db import models


# Create your models here.
class Config(models.Model):
    """Config model"""
    config_key = models.CharField(max_length=255) 
    config_value = models.TextField(blank=True, null=True)
    scope_level = models.CharField(max_length=7, blank=True, null=True)
    scope_id = models.IntegerField(blank=True, null=True)

    class Meta:
        """meta data"""
        db_table = 'config'
        constraints = [
            models.UniqueConstraint(fields=['config_key', 'scope_level', 'scope_id'], 
                                    name='config_values_uidx'), 
        ]

