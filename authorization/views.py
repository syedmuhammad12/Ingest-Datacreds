from django.shortcuts import render
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
import os, json, requests
from django.http import HttpResponse
from rest_framework import status
from authorization.models import Config
"""authorization view works as controller"""
# pylint: disable=too-few-public-methods
# pylint: disable=no-member
from base64 import b64decode
import json
import http.client
import os
import jwt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from django.db.models import Q, F, OuterRef, Subquery
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from users import models,serializers
# from users.serializers import UserSerializer
# from roles.models import Roles, Privileges
from authorization.models import Config
# from authorization.serializers import ConfigSerializer, CurrentRolePermissionSerializer
from data_ingestion import settings


class VerifyTenant:
    """To tenant verification class"""

    def __init__(self, key):
        """ initialisation """
        self.cursor = connection.cursor()
        self.key = key

    def decryption(self):
        """ String Decryption """
        rsa_key = RSA.importKey(
            open(os.path.dirname(__file__) + '/private.txt', "rb").read())
        cipher = PKCS1_v1_5.new(rsa_key)
        raw_cipher_data = b64decode(self.key)
        return cipher.decrypt(raw_cipher_data, 'sentinel')

    def GetTenant(self):
        """To get tenant name from master database """
        tenant = ""
        if self.key == "test_data_ingestion" or self.key == "default":
            tenant = "default"
        else:
            # data = (self.decryption()).decode("utf-8")
            data=self.key
            self.cursor.execute("SELECT * FROM TENANTS WHERE TENANT_STATUS= 1 "
                                "AND TENANT_CODE= '" + data + "'")
            row = self.cursor.fetchone()
        
            tenant = row[2]
        return tenant

    def getTenantAbbr(self):
        """To get tenant abbr from master database """
        if self.key == "test_simplesafety":
            return "default"
        else:
            data = (self.decryption()).decode("utf-8")
            self.cursor.execute("SELECT * FROM TENANTS WHERE TENANT_STATUS= 1 AND TENANT_CODE= '" + data + "'")
            row = self.cursor.fetchone()
            return row[7]



class EmailConfig(APIView):
    def get(self, request):
        try:
            config_data = Config.objects.filter(config_key='email_files')
            print(config_data)
            return Response()
        except Exception as e:
            print(e)
