import datetime
import subprocess
import zipfile

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from R2xml.jsonfile import R2XML
from R2xml import configuration as con
import glob
import os, shutil
import time
from r2import import configuration as conf
import json as j
from R2xml.main import R2XML_CIOMS
from R2xml.linelist import R2XML_LINELIST
from R2xml.litrature import R2XML_LITRATURE

from authorization.views import VerifyTenant
from django.http import HttpResponse
from R2xml.medwatch import R2XML_MEDWATCH
import boto3
from data_ingestion import settings
from smart_open import smart_open
import json
import requests


class R2xml(APIView):
    def post(self, request):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            data = request.data

            data = j.loads(j.dumps(data))
            print(data,'++++++++++')
            template = eval(data['json'][0])
            print(template["template_name"])
            if template['template_name'] == 'CIOMS':
                file_id = data['file_id']
                session = boto3.Session(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                s_3 = session.client('s3', settings.AWS_S3_REGION_NAME)

                cors_configuration = {
                    'CORSRules': [{
                        'AllowedHeaders': ['Authorization'],
                        'AllowedMethods': ['GET', 'PUT'],
                        'AllowedOrigins': ['*'],
                        'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                        'MaxAgeSeconds': 3000
                    }]
                }
                s_3.put_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                    CORSConfiguration=cors_configuration)

                s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/'+tenant+'/'
                html_page = s3_path + str(file_id) + '/2.json'
                src_file_path_html = s_3.generate_presigned_url(ClientMethod='get_object',
                                                                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                        'Key': html_page})
                response = requests.get(src_file_path_html)
                json = response.json()
            data = j.loads(j.dumps(data))
            df = {}
            res = data
            sender = res['sender']
            reciever = res['receiver']
            file_id = res['file_id']
            res = [eval(string) for string in res['json']]
            if template['template_name'] == 'CIOMS':
                for val in json:
                    df.update(val)
            else:
                for val in res:
                    df.update(val)

            xml_type = data['xml_type']

            json = df
            if len(json) > 0:
                if xml_type == 'R2':
                    if template["template_name"] == "IRMS":
                        data = R2XML(json, sender, reciever)
                    elif template["template_name"] == "CIOMS":
                        data = R2XML_CIOMS(json, sender, reciever)
                    elif template["template_name"] == "MedWatch":
                        session = boto3.Session(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                        s_3 = session.client('s3', settings.AWS_S3_REGION_NAME)

                        cors_configuration = {
                            'CORSRules': [{
                                'AllowedHeaders': ['Authorization'],
                                'AllowedMethods': ['GET', 'PUT'],
                                'AllowedOrigins': ['*'],
                                'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                                'MaxAgeSeconds': 3000
                            }]
                        }
                        s_3.put_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                            CORSConfiguration=cors_configuration)
                        s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/'+tenant+'/'

                        src_dir = s3_path + str(file_id) + '/1.json'
                        json_file_path = s_3.generate_presigned_url(ClientMethod='get_object',
                                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                            'Key': src_dir})


                        for line in smart_open(json_file_path, 'rb'):
                            json_data = line.decode('utf8')

                        page_arr = j.loads(json_data)


                        data = R2XML_MEDWATCH(page_arr['data'], sender, reciever)
                    list_of_files = glob.glob(con.r2xml_path + "*")
                    latest_file = max(list_of_files, key=os.path.getctime)
                    ss = 0
                    if ss == 1:
                        list_of_files = glob.glob(conf.logs_path + "*")
                        latest_file = max(list_of_files, key=os.path.getctime)
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            file = f.read()
                        return Response({"error": 1, "message": "errr"},
                                        status=status.HTTP_200_OK)
                    else:
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            file = f.read()
                            f.close()
                            if os.path.isfile(latest_file) or os.path.islink(latest_file):
                                os.unlink(latest_file)
                            return Response({"error": 0, "data": file}, status=status.HTTP_200_OK)

                if xml_type == 'R3':
                    if template["template_name"] == "IRMS":
                        data = R2XML(json, sender, reciever)
                    elif template["template_name"] == "CIOMS":
                        data = R2XML_CIOMS(json, sender, reciever)
                    elif template["template_name"] == "MedWatch":
                        session = boto3.Session(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                        s_3 = session.client('s3', settings.AWS_S3_REGION_NAME)

                        cors_configuration = {
                            'CORSRules': [{
                                'AllowedHeaders': ['Authorization'],
                                'AllowedMethods': ['GET', 'PUT'],
                                'AllowedOrigins': ['*'],
                                'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                                'MaxAgeSeconds': 3000
                            }]
                        }
                        s_3.put_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                            CORSConfiguration=cors_configuration)
                        s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/'+tenant+'/'

                        src_dir = s3_path + str(file_id) + '/1.json'
                        json_file_path = s_3.generate_presigned_url(ClientMethod='get_object',
                                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                            'Key': src_dir})

                        for line in smart_open(json_file_path, 'rb'):
                            json_data = line.decode('utf8')

                        page_arr = j.loads(json_data)
                        # print(page_arr['data'])
                        data = R2XML_MEDWATCH(page_arr['data'], sender, reciever)
                    list_of_files = glob.glob(con.r2xml_path + "*")
                    latest_file = max(list_of_files, key=os.path.getctime)
                    filename = latest_file.split('\R2_')[1]
                    shutil.copy(latest_file,
                                os.path.join(con.bfc_path, 'r2', filename))
                    if os.path.isfile(latest_file) or os.path.islink(latest_file):
                        os.unlink(latest_file)
                    result = subprocess.run(
                        [
                            os.path.join(con.bfc_path, "R3.bat")
                        ],
                        capture_output=True
                    )
                    if result.stderr == b'':
                        latest_file = os.path.join(con.bfc_path, 'r3', filename)
                        file_data = ""
                        with open(latest_file, 'r') as file:
                            file_data = file.read()
                            file.close()
                        if os.path.isfile(latest_file) or os.path.islink(latest_file):
                            os.unlink(latest_file)
                        return Response({'data': file_data, "error": 0}, status=status.HTTP_200_OK)

            return Response({"error": 1}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class R2xmlLineList(APIView):
    def post(self, request):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            data = request.data
            R2XML_LINELIST(data, tenant)
            xml_type = data['xml_type']
            if xml_type == "R2":
                print("here")
                folder_to_zip = os.path.dirname(__file__) + '/linelist/' + tenant + '/' + str(
                    data['file_id']) + '/r2xml/'

                zip_file_name = os.path.dirname(__file__) + '/linelist/' + tenant + '/' + str(
                    data['file_id']) + "/1.zip"

                with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
                    for root, _, files in os.walk(folder_to_zip):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_to_zip).encode('utf-8',
                                                                                       'surrogateescape').decode(
                                'utf-8')
                            zipf.write(file_path, arcname=arcname)
                FilePointer = open(zip_file_name, "rb")
                response = HttpResponse(FilePointer, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=1.zip'
                return response
            if xml_type == "R3":
                src = os.path.dirname(__file__) + '/linelist/' + tenant + '/' + str(
                    data['file_id']) + '/r2xml'
                for root, _, files in os.walk(src):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # print(file_path)
                        filename = "R3_" + file_path.split('\R2_')[1]
                        shutil.copy(file_path,
                                    os.path.join(con.bfc_path, 'r2', filename))
                folder_to_zip = os.path.join(con.bfc_path, 'r3')
                for root, _, files in os.walk(folder_to_zip):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)

                result = subprocess.run(
                    [
                        os.path.join(con.bfc_path, "R3.bat")
                    ],
                    capture_output=True
                )

                if result.stderr == b'':


                    zip_file_name = os.path.join(con.bfc_path, 'r3', "1.zip")

                    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
                        for root, _, files in os.walk(folder_to_zip):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, folder_to_zip).encode('utf-8',
                                                                                           'surrogateescape').decode(
                                    'utf-8')
                                zipf.write(file_path, arcname=arcname)

                    FilePointer = open(zip_file_name, "rb")
                    response = HttpResponse(FilePointer, content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename=1.zip'

                    return response

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class R2xmlLitrature(APIView):
    def downloadXML(self, json=[], relation_json=[], customer_db="default", sender=0, receiver=0, xml_type=""):
        try:
            if len(json) != 0:
                stat = R2XML_LITRATURE(json, relation_json, customer_db, sender, receiver, xml_type)

                if stat.error_message == 'r2_created':
                    latest_file = "{}{}".format(con.r2xml_path, stat.r2_filename)
                    if xml_type == 'R2':
                        file_data = ""
                        with open(latest_file, 'r') as file:
                            file_data = file.read()
                            file.close()
                        # if os.path.isfile(latest_file) or os.path.islink(latest_file):
                        #     os.unlink(latest_file)
                        return {'file_name': str(os.path.basename(latest_file)), 'data': file_data, "error": 0}

                    if xml_type == 'R3':
                        print(latest_file)
                        print(os.path.join(con.bfc_path, 'r2', stat.r2_filename))
                        shutil.copy(latest_file,
                                    os.path.join(con.bfc_path, 'r2', stat.r2_filename))
                        if os.path.isfile(latest_file) or os.path.islink(latest_file):
                            os.unlink(latest_file)
                    #
                    # file_names = dict()
                    # if xml_type == 'R2_and_R3':
                    #     if settings.USE_S3 == True:
                    #         file = open(latest_file, 'r')
                    #         self.upload_file_to_s3bucket('r2', os.path.basename(latest_file), file)
                    #     else:
                    #         shutil.copy(latest_file, os.path.join(settings.STATICFILES_LOCAL, 'data', 'r2',
                    #                                               os.path.basename(latest_file)))
                    #     file_names['r2'] = "r2/{}".format(str(os.path.basename(latest_file)))
                    #     if os.path.isfile(latest_file) or os.path.islink(latest_file):
                    #         os.unlink(latest_file)
                    #
                    if xml_type == 'R3' or xml_type == 'R2_and_R3':
                        result = subprocess.run(
                            [
                                os.path.join(con.bfc_path, "R3.bat")
                            ],
                            capture_output=True
                        )
                        if result.stderr == b'':
                            # old_file = os.path.join(settings.STATICFILES_LOCAL, 'data', 'r2', stat.r2_filename)
                            # if os.path.isfile(old_file) or os.path.islink(old_file):
                            #     os.unlink(old_file)
                            latest_file = os.path.join(con.bfc_path, 'r3', stat.r2_filename)
                            r3_filename = "R3_XML_{}.xml".format(con.bfc_path, 'r3', stat.r2_filename)
                            #
                            #         if xml_type == 'R2_and_R3':
                            #             if settings.USE_S3 == True:
                            #                 file = open(latest_file, 'r')
                            #                 self.upload_file_to_s3bucket('r3', r3_filename, file)
                            #
                            #             file_names['r3'] = "r3/{}".format(r3_filename)
                            #             return {'file_name': file_names, 'data': "", "error": 0}
                            #
                            file_data = ""
                            with open(latest_file, 'r') as file:
                                file_data = file.read()
                                file.close()
                            if os.path.isfile(latest_file) or os.path.islink(latest_file):
                                os.unlink(latest_file)
                            return {'file_name': str(r3_filename), 'data': file_data, "error": 0}
                        return {'file_name': "", 'data': str(result.stderr), "error": 1}
                else:
                    return {"file_name": "", "data": "XML GENERATION ERROR", "error": 1}
            else:
                return {"file_name": "", "data": "JSON ERROR", "error": 1}
        except Exception as e:
            return {"file_name": "", "data": str(e), "error": 1}
