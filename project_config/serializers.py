from rest_framework import serializers
from .models import Email,Sharepoint

class Emailserializer(serializers.ModelSerializer):
    class Meta:
        model=Email
        fields='__all__'
        
class Sharepointserializer(serializers.ModelSerializer):
    class Meta:
        model=Sharepoint
        fields='__all__'