from rest_framework import serializers
from .models import User

class userserializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","user_id","user_name","email","role","company_id","status"]


