import csv
import time

from django.shortcuts import render
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
import boto3
import os, json, requests
from django.http import HttpResponse
from rest_framework import status
from data_ingestion import settings
from pdf2image import convert_from_path
from file_management.serializers import CreateFileSerializer, FileListSerializer
from file_management.models import File, DuplicateFilesTrack
from file_templates.models import FileTemplatesModel
from project_config.models import Email, Sharepoint
from project_config.serializers import Emailserializer, Sharepointserializer
from smart_open import smart_open
from structured_doc.views import ExtractTrainData
from configuration.aws import *
import pandas as pd
from structured_doc.detect_checkbox import check_box_detect
from structured_doc.pdf_to_html import html_blocks
import pdftotree
from authorization.views import VerifyTenant
import datetime
from file_templates.models import FileTemplatesModel
from configuration.aws import S3Bucket
import pytesseract
import pdf2image
from PIL import Image
import cv2
import mysql.connector
from configuration.config import Config

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
CLIENT_ID = 'f27d7a47-37e7-4725-93c3-09ebffc92621'
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
CLIENT_SECRET = 'vZV8Q~pXSG0O5drf6WNcbo5KNLoc3YlwGPV10bIt'
GRANT_TYPE = 'client_credentials'
SHAREPOINT_DIR = 'C:\qinecsa\python_projects\data_indigestion/rest_api/data_ingestion/file_management/sharepoint_files'
EMAIL_DIR = 'C:\qinecsa\python_projects\data_indigestion/rest_api/data_ingestion/file_management/email_attachments'

SCOPE = 'https://graph.microsoft.com/.default'
SCOPES = ['Mail.ReadWrite']
TENANT_ID = '45472cbd-1c2f-4f2d-af99-2231bbd5f002'
email_id = "littrace.req@qinecsa.com"
EMAIL_FETCH_COUNT = 20


# Create your views here.


class ConvertPDFtoImage(APIView):

    def get(self, request):
        try:

            path = 'C:\qinecsa\python_projects\data_indigestion/rest_api/data_ingestion/file_management/file_conversions/'
            for i in range(298, 348):
                images = convert_from_path(path + str(i) + "/1.pdf", size=(1700, 2200))
                for index, image in enumerate(images):
                    image.save(f'{path + str(i) + "/"}{index}.png')

            return Response("", status=status.HTTP_201_CREATED)
        except Exception as exc:
            print(exc)


class FileUpload(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("file upload", request.data)
            # print(type(int(request.data['size'])))
            # exit(1)
            # print("vars", vars(request.data))
            result_data = []
            if request.data:
                for index in range(int(request.data['size'])):
                    try:
                        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
                        files = self.create(tenant, request.data, str(index))
                        if files.id_file > 0:
                            # file_serializer.save(using=tenant)
                            # print(files)
                            # print(vars(files))
                            result_records = FileListSerializer(files).data
                            result_data.append(result_records)
                            # print(result_records)
                            m_fdata = result_records['file_template_id']
                            template_name = ""
                            for key, value in m_fdata.items():
                                if key == 'template_name':
                                    template_name = value
                            id_file = files.id_file

                            edited_file_name = (request.data.get(str(index) + '_file_name').name)
                            print(edited_file_name)
                            file_ext = os.path.splitext(edited_file_name)[1]

                            page_count = 1

                            if file_ext.lower() == '.pdf':
                                # time.sleep(1)
                                target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
                                target_file_path = target_file_path + '/uploads/' + tenant + '/' + str(
                                    id_file) + "/" + edited_file_name
                                # s_3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                #                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                                print('target_file_path', target_file_path)
                                # create a directory
                                UPLOADS_DIR = os.path.dirname(__file__) + '/file_uploads/' + tenant + '/'
                                if not os.path.exists(UPLOADS_DIR + str(id_file)):
                                    os.makedirs(UPLOADS_DIR + str(id_file))

                                print()
                                file_content = request.FILES[f"{index}_file"]
                                with open(f"{UPLOADS_DIR}{id_file}/{edited_file_name}", "wb") as f:
                                    f.write(file_content.read()) 
                                # upload to local storage
                                # s_3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).download_file(UPLOADS_DIR + str(id_file) + "/" + edited_file_name, target_file_path
                                #                                                            )
                                
                                print("hehe")
                                # convert pdf to image
                                if template_name == "MedWatch":
                                    images = convert_from_path(UPLOADS_DIR + str(id_file) + "/" + edited_file_name,
                                                               size=(3400, 4400))
                                    # images = pdf2image.convert_from_bytes(file_data.read(), fmt="png", size=(3400, 2200))
                                    rename_flag = False  # This flag will be True once we encounter the first image with "PATIENT INFORMATION"
                                    next_image_name = 1  # Start renaming from 1.png
                                    for index, image in enumerate(images):
                                        content = pytesseract.image_to_string(image)
                                        # if index != 0:
                                        # if index != 0 and index != 1:
                                        if "PATIENT INFORMATION" in content and "ALL MANUFACTURERS" in content or rename_flag:
                                            rename_flag = True  # Set the flag to True to rename subsequent images
                                            image.save(f'{UPLOADS_DIR + str(id_file) + "/page_"}{next_image_name}.png')
                                            page_count = page_count + 1
                                            print(f"Image {id_file} processed and copied as '{next_image_name}.png'.")
                                            next_image_name += 1
                                        else:
                                            print(
                                                f"Image {id_file} processed. Does not contain 'PATIENT INFORMATION' and not copied.")

                                    print("All images processed.")

                                else:
                                    images = convert_from_path(UPLOADS_DIR + str(id_file) + "/" + edited_file_name,
                                                               size=(1700, 2200),
                                                               poppler_path="./../poppler-0.68.0/bin")
                                    for index, image in enumerate(images):
                                        image.save(f'{UPLOADS_DIR + str(id_file) + "/page_"}{index + 1}.png')
                                        page_count = page_count + 1

                                target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION

                                s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME,
                                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                                if m_fdata["file_type"] != "Unstructured" and template_name != "MedWatch":
                                    pdf_str = pdftotree.parse(UPLOADS_DIR + str(id_file) + "/" + edited_file_name,
                                                              UPLOADS_DIR + str(id_file) + "/" + "1.html",
                                                              model_type=None, model_path=None, visualize=False)

                                # iterate and upload all files to s3 bucket
                                for root, dirs, files in os.walk(UPLOADS_DIR + str(id_file)):
                                    for file in files:
                                        print(file)
                                        s3.upload_file(os.path.join(root, file), settings.AWS_STORAGE_BUCKET_NAME,
                                                       target_file_path + '/uploads/' + tenant + '/' + str(
                                                           id_file) + "/" + file)
                                page_count = page_count - 1

                            file = File.objects.using(tenant).get(id_file=id_file)
                            file.file_name = 'uploads/' + str(id_file) + '/' + edited_file_name
                            file.file_type = 'Upload'
                            file.pdf_page_count = page_count
                            file.save(using=tenant)
                    except Exception as e:
                        print('inside loop', e)
                return Response(result_data, status=status.HTTP_201_CREATED)
            return Response("Null requested data", status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            print(exc)
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)

    def create(self, tenant, data, index):
        print("create", tenant)
        result = FileTemplatesModel.objects.using(tenant).get(template_id=data[index + '_file_template_id'])
        mydb = mysql.connector.connect(
            host=Config.DATABASE_HOST,
            user=Config.DATABASE_USER,
            password=Config.DATABASE_PASSWORD,
            database=Config.DATABASE_NAME
        )
        mycursor = mydb.cursor()
        mycursor.execute(f"""INSERT INTO `file_management` (original_file_name, file_template_id, file_format, file_size,
                         is_delete, file_name) VALUES ('{data[index + "_original_file_name"]}', %s, '{data[index + "_file_format"]}',
                         '{str(data[index + "_file_size"]) + '__' + tenant}', '{data[index + "_is_delete"]}', '{data[index + "_file_name"]}')""", (int(result.template_id),))
        
        # p = File(original_file_name=data[index + '_original_file_name'], file_template_id=result,
        #          file_format=data[index + '_file_format'],
        #          file_size=str(data[index + '_file_size']) + '__' + tenant, is_delete=data[index + '_is_delete'],
        #          file_name=data[index + '_file_name'])
        # print(p)
        # p.save(using=tenant)
        mydb.commit()
        mydb.close()
        file_data = File.objects.using(tenant).latest('id_file')
        print("save", file_data)
        return file_data


class EmailAttachmentsDownload(APIView):
    def get(self, request):
        for value in range(len(self.get_details())):
            email_id = self.get_details()[value]['email_id']
            access_token = self.get_access_token(value)
            headers = {
                'Authorization': 'Bearer ' + access_token['access_token']
            }
            params = {
                'top': EMAIL_FETCH_COUNT,  # max is 1000 messages per request
                'select': 'subject,hasAttachments',
                'filter': 'hasAttachments eq true',
                'count': 'true'
            }

            response = requests.get(GRAPH_API_ENDPOINT + '/users/' + email_id + '/mailFolders/Inbox/messages',
                                    headers=headers, params=params)

            if response.status_code != 200:
                raise Exception(response.json())

            response_json = response.json()
            emails = response_json['value']
            email_count = 0

            for email in emails:
                if email['hasAttachments']:
                    email__id = email['id']

                    # Check if email downloaded
                    if DuplicateFilesTrack.objects.filter(file_id=email__id).exists():
                        pass
                    else:
                        # Insert in table to avoid future email duplication
                        email_count = email_count + 1
                        m_data = DuplicateFilesTrack(download_type='email')
                        m_data.file_id = email__id
                        m_data.save()
                        self.download_email_attachments(email__id, headers, email_id)

            if email_count == 0:
                response_data = {
                    "status_code": 200,
                    "error": 0,
                    "message": "Up To Date",
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

            else:
                response_data = {
                    "status_code": 200,
                    "error": 0,
                    "message": "Email Attachments fetched successfully",
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

    def get_details(self):
        email = Email.objects.all()
        serializer = Emailserializer(email, many=True)
        data = serializer.data
        return data

    # this function download_email_attachments
    def download_email_attachments(self, message_id, headers, email_id):
        AWS_KEY_ID = 'AKIAW3GZXGRDWQCHJYXB'
        AWS_SECRET = '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'

        try:

            response = requests.get(
                GRAPH_API_ENDPOINT + '/users/' + email_id + '/messages/{0}/attachments'.format(message_id),
                headers=headers
            )
            if response.status_code != 200:
                raise Exception(response.json())

            attachment_items = response.json()['value']
            for attachment in attachment_items:
                file_name = attachment['name']
                attachment_id = attachment['id']
                attachment_content = requests.get(
                    GRAPH_API_ENDPOINT + '/users/' + email_id + '/messages/{0}/attachments/{1}/$value'.format(
                        message_id, attachment_id),
                    headers=headers
                )

                if file_name.endswith('pdf') or file_name.endswith(
                        'png'):  # currently download pdf attachments ony to the local.

                    file = File(original_file_name=file_name)
                    file.file_format = 'application/pdf'
                    file.file_size = ''
                    file.is_delete = 0
                    file.save()

                    file_id = File.objects.latest('id_file')
                    id_file = file_id.id_file

                    # create a directory
                    if not os.path.exists(EMAIL_DIR + "/" + str(id_file)):
                        os.makedirs(EMAIL_DIR + "/" + str(id_file))

                    print('Saving file {0}...'.format(file_name))
                    file_ext = os.path.splitext(file_name)[1]
                    edited_file_name = "1" + file_ext

                    with open(os.path.join(EMAIL_DIR + "/" + str(id_file), edited_file_name), 'wb') as _f:
                        _f.write(attachment_content.content)

                    # if file_name.endswith('pdf'):
                    #     # convert pdf to image
                    #     images = convert_from_path(EMAIL_DIR + "/" + str(id_file) + "/" + edited_file_name)
                    #     for index, image in enumerate(images):
                    #         image.save(f'{EMAIL_DIR + "/" + str(id_file) + "/"}{index}.png')

                    target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION

                    s3 = boto3.client("s3",
                                      region_name=settings.AWS_S3_REGION_NAME,
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

                    # iterate and upload all files to s3 bucket
                    for root, dirs, files in os.walk(EMAIL_DIR + "/" + str(id_file)):
                        for file in files:
                            s3.upload_file(os.path.join(root, file), settings.AWS_STORAGE_BUCKET_NAME,
                                           target_file_path + '/uploads/' + str(id_file) + "/" + file)

                    file = File.objects.get(id_file=id_file)
                    file.file_name = 'uploads/' + str(id_file) + '/' + edited_file_name
                    file.file_type = 'Email'
                    file.save()

                    # os.unlink(EMAIL_DIR + "/" + str(id_file))
            return True
        except Exception as e:
            print(e)
            return False

    # this function helps to access the token.
    def get_access_token(self, value):
        url = "https://login.microsoftonline.com/" + self.get_details()[value]['Tenant_id'] + "/oauth2/v2.0/token"
        payload = 'client_id=' + self.get_details()[value][
            'client_id'] + '&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=' + \
                  self.get_details()[value]['client_secret'] + '&grant_type=' + GRANT_TYPE
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'fpc=AmUzsZHzm2tPv1bycXTjJDZwbag-AQAAABhM_NoOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()


class SharePointFilesDownload(APIView):
    def get(self, request):
        for value in range(len(self.get_details())):
            file_count = 0
            # host_name = 'qinecsa.sharepoint.com'
            host_name = self.get_details()[value]['host_name']
            # site_name = 'DataIngestion'
            site_name = self.get_details()[value]['site_name']
            site_uri = f'{GRAPH_API_ENDPOINT}/sites/{host_name}:/sites/{site_name}'
            site_id = self.make_request(site_uri, value).get('id', {})
            drive_uri = f'{GRAPH_API_ENDPOINT}/sites/{site_id}/drives'
            drives = self.make_request(drive_uri, value)
            drive_id = ''
            for item in drives.get('value', []):
                if item.get('name') == "Documents":
                    drive_id = item.get('id')

            items_uri = ''
            while True:
                # First page
                if items_uri == '':
                    items_uri = f'{GRAPH_API_ENDPOINT}/sites/{site_id}/drives/{drive_id}/root/children'
                    items = self.make_request(items_uri, value)
                    # print(items)
                    self.download_the_files(items, file_count)
                    items_uri = items.get('@odata.nextLink')

                # All other pages
                else:
                    items = self.make_request(items_uri, value)
                    self.download_the_files(items, file_count)
                    items_uri = items.get('@odata.nextLink')

                # No more pages found
                if items_uri is None:
                    break

            if file_count == 0:
                response_data = {
                    "status_code": 200,
                    "error": 0,
                    "message": "Up To Date",
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    "status_code": 200,
                    "error": 0,
                    "message": "Sharepoint Files downloaded successfully",
                }
                return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

    def make_request(self, url, value):
        access_token = self.get_access_token(value)
        headers = {
            'Authorization': 'Bearer ' + access_token['access_token']
        }
        r = requests.get(url, headers=headers)
        return r.json()

    def get_access_token(self, value):
        url = "https://login.microsoftonline.com/" + self.get_details()[value]['Tenant_id'] + "/oauth2/v2.0/token"
        payload = 'client_id=' + self.get_details()[value][
            'client_id'] + '&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=' + \
                  self.get_details()[value]['client_secret'] + '&grant_type=' + GRANT_TYPE
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'fpc=AmUzsZHzm2tPv1bycXTjJDZwbag-AQAAABhM_NoOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def get_details(self):
        sharepoint = Sharepoint.objects.all()
        serializer = Sharepointserializer(sharepoint, many=True)
        data = serializer.data
        return data

    def download_the_files(self, items, file_count):
        AWS_KEY_ID = 'AKIAW3GZXGRDWQCHJYXB'
        AWS_SECRET = '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'

        for file in items.get('value', []):
            file_name = file.get('name')
            file_download = file.get('@microsoft.graph.downloadUrl')

            if DuplicateFilesTrack.objects.filter(file_id=file_name).exists():
                pass
            else:
                file_count = file_count + 1
                m_data = DuplicateFilesTrack(download_type='sharepoint')
                m_data.file_id = file_name
                m_data.save()

                file_data = File(original_file_name=file_name)
                file_data.file_format = "application/pdf"
                file_data.file_size = ""
                file_data.is_delete = 0
                file_data.file_type = 'Sharepoint'
                file_data.save()

                file_id = File.objects.latest('id_file')
                id_file = file_id.id_file

                # create a directory
                if not os.path.exists(SHAREPOINT_DIR + "/" + str(id_file)):
                    os.makedirs(SHAREPOINT_DIR + "/" + str(id_file))

                # download files
                response = requests.get(file_download)
                file_ext = os.path.splitext(file_name)[1]
                edited_file_name = "1" + file_ext
                save_to_path = os.path.join(SHAREPOINT_DIR + "/" + str(id_file), edited_file_name)
                with open(save_to_path, "wb") as f:
                    f.write(response.content)
                    print('saved')

                # if file_name.endswith('pdf'):
                #     # convert to image
                #     images = convert_from_path(SHAREPOINT_DIR + "/" + str(id_file) + "/" + edited_file_name)
                #     for index, image in enumerate(images):
                #         image.save(f'{SHAREPOINT_DIR + "/" + str(id_file) + "/"}{index}.png')

                target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
                s3 = boto3.client("s3",
                                  region_name=settings.AWS_S3_REGION_NAME,
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

                # iterate and upload all files to s3 bucket
                for root, dirs, files in os.walk(SHAREPOINT_DIR + "/" + str(id_file)):
                    for m_file in files:
                        s3.upload_file(os.path.join(root, m_file), settings.AWS_STORAGE_BUCKET_NAME,
                                       target_file_path + '/uploads/' + str(id_file) + "/" + m_file)

                file_data = File.objects.get(id_file=id_file)
                file_data.file_name = 'uploads/' + str(id_file) + '/' + edited_file_name
                file_data.save()
                # os.unlink(SHAREPOINT_DIR + "/" + str(id_file))


class FileListing(APIView):
    def post(self, request):
        try:
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            data = json.loads(request.body)['data']
            try:
                filter_by = data['filter_by']
            except Exception:
                filter_by = {}

            order_column = 'id_file'
            if order_column:
                order_column = data['order_by']

            sort_order = data['sort_order']
            if sort_order == 'desc':
                order_column = '-' + order_column

            start_index = data['start_index'] - 1
            page_size = data['page_size'] + start_index
            queryset = File.objects.filter(**filter_by).using(tenant).order_by(order_column)
            result_records = FileListSerializer(queryset[start_index: page_size], many=True).data
            response_data = {
                "status_code": 200,
                "error": 0,
                "data": result_records,
                "total_records": len(queryset)
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            response_data = {
                'message': 'Something went wrong',
                'error': "1",
                'status_code': 404
            }
            return Response(response_data, status=404)


class ConvertPdfToImage(APIView):
    def get(self, request):
        pdf_path = 'C:\qinecsa\python_projects\data_indigestion/rest_api/data_ingestion/file_management/email_attachments/Ayoob RM_2022.pdf';
        images = convert_from_path(pdf_path)
        for index, image in enumerate(images):
            image.save(f'{pdf_path}-{index}.png')


class ViewFile(ExtractTrainData):
    def get(self, request, file_id, page_no):
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        file_data = File.objects.using(tenant).get(id_file=file_id)
        template_name = ""
        result_records = FileListSerializer(file_data).data
        m_fdata = result_records['file_template_id']
        for key, value in m_fdata.items():
            if key == 'template_name':
                template_name = value

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
        s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/' + tenant + '/'
        if result_records['file_format'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            response_data = {
                'template_name': template_name,
                'file_data': result_records,
                'error': "0",
                "file_format": result_records['file_format'],
                'status_code': 200
            }
            return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
        elif result_records['file_format'] == 'image/png':
            src_dir = s3_path + str(file_id) + '/1.png'
        elif result_records['file_format'] == 'application/pdf':
            src_dir = s3_path + str(file_id) + '/page_' + str(page_no) + '.png'
        elif result_records['file_format'] == 'image/jpeg':
            src_dir = s3_path + str(file_id) + '/1.jpeg'
        src_file_path = s_3.generate_presigned_url(ClientMethod='get_object',
                                                   Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                           'Key': src_dir})

        checkbox_data = ""
        if template_name != 'IRMS' and m_fdata['file_type'] == "Structured":
            try:
                if page_no == 1:
                    if template_name == 'MedWatch':
                        print("checkbox")
                        checkbox_data = check_box_detect(src_file_path, template_name, file_id,
                                                         page_no,tenant).find_checkbox_result_medwatch()
                    else:
                        checkbox_data = check_box_detect(src_file_path, template_name, file_id, page_no,
                                                         tenant).find_nearest_checkbox_and_detect()
            except Exception as e:
                e


        from_second_page = ""
        second_page_data = ""
        try:
            if template_name == 'IRMS':
                if result_records['file_format'] == 'application/pdf':
                    html_page = s3_path + str(file_id) + '/1.html'
                    src_file_path_html = s_3.generate_presigned_url(ClientMethod='get_object',
                                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                            'Key': html_page})
                    # by default below varaible will be zero it will consider cioms. if made equal to 1
                    # then it will take irms keys
                    irms = 1
                    from_second_page = html_blocks(src_file_path_html, page_no, irms).get_html_blocks()

            elif template_name == 'CIOMS':
                if result_records['file_format'] == 'application/pdf':
                    html_page = s3_path + str(file_id) + '/1.html'
                    src_file_path_html = s_3.generate_presigned_url(ClientMethod='get_object',
                                                                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                            'Key': html_page})

                    from_second_page = html_blocks(src_file_path_html, page_no, 0).get_html_blocks()
            elif template_name == 'MedWatch':
                if result_records['file_format'] == 'application/pdf':
                    second_page_data = self.extract_second_page(file_id, page_no, template_name,tenant)
        except Exception as e:
            print("exception---", e)
        # get json file
        json_data = ""
        # if template_name != 'IRMS':
        if page_no == 1 and m_fdata['file_type'] == "Structured":
            if result_records['is_data_extracted'] == "1":
                src_dir = s3_path + str(file_id) + '/1.json'
                json_file_path = s_3.generate_presigned_url(ClientMethod='get_object',
                                                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': src_dir})

                for line in smart_open(json_file_path, 'rb'):
                    json_data = line.decode('utf8')

            else:
                json_data = self.extract_cordinates(file_id, page_no, template_name, tenant)
        # print("Medwatch")
        # print(json_data)
        # print(checkbox_data)
        # print(second_page_data)
        # exit(1)
        try:
            if template_name == 'MedWatch':
                page_one_arr = json.loads(json_data)

                filter_json_data = []
                # Iterate through the "data" array and extract "key" and "value" fields
                for item in page_one_arr["data"]:
                    key = item["key"]
                    value = item["value"]
                    print(item)
                    key_text = str(key['key_name'])
                    value_text = str(value['text'])
                    # co_ord = item["co_ord"] if "co_ord" in item and item["co_ord"] else item.get("cordinates_name", None)
                    co_ord = key["cordinates_name"]
                    # print(key_text)
                    # print(value_text)
                    # print(co_ord)

                    json_arr = {
                        'key': key_text,
                        'value': value_text,
                        'co_ord': co_ord
                    }
                    filter_json_data.append(json_arr)

                task = {
                    'data': filter_json_data
                }
                json_string = json.dumps(task, default=self.np_encoder)
                # print("****************8")
                # print(json_string)
                # Parse the JSON arrays
                page_two_data = json.loads(second_page_data)
                page_one_data = json.loads(json_string)
                page_one_checkbox_data = json.loads(checkbox_data)

                # return

                # Combine the "data" arrays from data1 and data2 into a single array
                # combined_data = {
                #     "data": (page_one_data["data"] if page_one_data["data"] else [])+ (page_two_data["data"] if page_two_data["data"] else []) + (page_one_checkbox_data["data"] if page_one_checkbox_data["data"] else [])
                # }

                # Filter out empty arrays
                non_empty_arrays = [data["data"] for data in [page_one_data, page_two_data, page_one_checkbox_data] if
                                    data["data"]]

                # Combine non-empty arrays
                combined_data = {"data": sum(non_empty_arrays, [])}

                # print(combined_data)
                # return
                # Convert the combined data to a JSON string
                # result_json = json.dumps(combined_data, indent=4)

                # Convert the concatenated list back to JSON
                result_json = json.dumps(combined_data)

                # print()

                # print(combined_data)
                # print("******************")
                # print(result_json)
                with open(str(file_id) + '_medwatch_file.json', mode='w') as f:
                    f.write(result_json)
                # return

                edited_file_name = '1.json'
                target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/' + tenant + '/'
                target_file_path = target_file_path + str(file_id) + "/" + edited_file_name
                s3 = boto3.client("s3",
                                  region_name=settings.AWS_S3_REGION_NAME,
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

                s3.upload_file(str(file_id) + '_medwatch_file.json', settings.AWS_STORAGE_BUCKET_NAME,
                               target_file_path)
        except Exception as e:
            print("medwath json", e)

        csv_file_path = ""
        if template_name == 'CIOMS':
            # get key names
            csv_file_path = os.path.abspath("..") + "/data_ingestion/structured_doc/key_files/cimos_key_file.xlsx"

        elif template_name == 'IRMS':
            # get key names
            csv_file_path = os.path.abspath("..") + "/data_ingestion/structured_doc/key_files/irms_key_file.xlsx"

        elif template_name == 'MedWatch':
            # get key names
            csv_file_path = os.path.abspath("..") + "/data_ingestion/structured_doc/key_files/medwatch_key_file.xlsx"

        key_names = []
        if csv_file_path != "":
            dataframe = pd.read_excel(csv_file_path)
            for index, row in dataframe.iterrows():
                co_ordinates = row['cordinates']
                if co_ordinates not in key_names:
                    key_names.append(co_ordinates)

        response_data = {
            'template_name': template_name,
            'key_names': key_names,
            'data': src_file_path,
            'json_data': json_data,
            'check_box_data': json.dumps(checkbox_data, default=self.np_encoder),
            'from_second_page': str(from_second_page),
            'second_page_data': second_page_data,
            'file_data': result_records,
            'page_count': result_records['pdf_page_count'],
            'error': "0",
            'is_data_extracted': result_records['is_data_extracted'],
            'status_code': 200
        }
        print("response data", response_data)
        return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)


class UploadExtractedData(ExtractTrainData, APIView):
    def post(self, request, file_id):
    
        tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
        uploaded_file = request.FILES.get('file_name')
        print(file_id, uploaded_file)
        template_id = File.objects.using(tenant).filter(id_file=file_id).values()[0]['file_template_id_id']
        template_name = FileTemplatesModel.objects.using(tenant).filter(template_id=template_id).values()[0][
            'template_name']  # read uploaded json file
        str_text = ""
        print()
        for line in uploaded_file:
            str_text = str_text + line.decode()

        # convert json to object
        json_obj = json.loads(str_text)

        csv_file_path = os.path.abspath("..") + "/data_ingestion/structured_doc/key_files/cimos_key_file.xlsx"
        df = pd.read_excel(csv_file_path)
        existing_length = len(df.axes[0])

        # add newly identified key names in the key xlsx file
        key_name_list = []
        key_list = []
        for i in range(len(json_obj)):
            if 'key_name' in json_obj[i]:
                # write key in key file
                values = df['keywords'].unique()
                if json_obj[i]['key'] not in values:
                    key_name_list.append(json_obj[i]['key_name'])
                    key_list.append(json_obj[i]['key'])

        dataframe = pd.DataFrame({
            'keywords': list(key_list),
            'cordinates': list(key_name_list)
        })

        with pd.ExcelWriter(csv_file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            dataframe.to_excel(writer, header=False, index=False, sheet_name="Sheet1",
                                startrow=(existing_length + 1))

        # add newly identified co-ordinates in dataset file
        csv_file_path = os.path.abspath("..") + "/data_ingestion/structured_doc/key_files/cimos_cordinates.xlsx"
        df = pd.read_excel(csv_file_path)
        for i in range(len(json_obj)):
            if 'key_name' in json_obj[i]:
                key_name = json_obj[i]['key_name']
                values = df[key_name].unique()
                co_ordinate = str(str(json_obj[i]['Xmin']) + ":" + str(json_obj[i]['Ymin']) + ":" +
                                    str(json_obj[i]['Xmax']) + ":" + str(json_obj[i]['Ymax']))
                if co_ordinate not in values:
                    print(key_name + "--" + co_ordinate)
                    json_obj[i].pop('key_name')
                    json_obj[i].pop('confidence_score')
                    print(json_obj[i])

                    df = pd.read_excel(csv_file_path)
                    existing_length = df[key_name].count()
                    column_index = df.columns.get_loc(key_name)

                    print(column_index)

                    dataframe = pd.DataFrame({
                        key_name: [co_ordinate]
                    })

                    with pd.ExcelWriter(csv_file_path, mode='a', engine='openpyxl',
                                        if_sheet_exists='overlay') as writer:
                        dataframe.to_excel(writer, header=False, index=False, sheet_name="Sheet1",
                                            startrow=(existing_length + 1), startcol=column_index)

        f = open("temp_file.json", "w")
        f.write(json.dumps(json_obj))
        f.close()
        if template_name == "CIOMS":
            target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
            id_file = file_id

            # extracting HTML blocks from second page
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

            s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/' + tenant + '/'
            html_page = s3_path + str(file_id) + '/1.html'
            src_file_path_html = s_3.generate_presigned_url(ClientMethod='get_object',
                                                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': html_page})
            print("html page:", html_page)
            print("html file:", src_file_path_html)
            from_second_page = html_blocks(src_file_path_html, 1, 0).get_html_blocks()

            # extracting checkbox
            checkbox_data = []
            try:
                s3_path = settings.AWS_PUBLIC_MEDIA_LOCATION + '/uploads/' + tenant + '/'
                page_1_png_file = s3_path + str(id_file) + "/" + "page_1.png"
                print("here")
                src_file_path = s_3.generate_presigned_url(ClientMethod='get_object',
                                                            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': page_1_png_file})
                # print("here2")
                print("file path:", src_file_path)
                print("temp name:", template_name)
                checkbox = check_box_detect(src_file_path, template_name, file_id,
                                            1, tenant).find_nearest_checkbox_and_detect()
                print(checkbox_data)
                for i in checkbox:
                    checkbox_data.append({'key': i['key'], 'value': i['values']})
                for i in checkbox_data:
                    json_obj.append(i)
                print(json_obj)
            except Exception as e:
                print("error",e)

            # extracting png data from second page
            target_file_path = 'uploads/' + tenant + '/' + str(id_file) + "/" + "1.pdf"
            file_data = self.load_s3bucket_file(str(target_file_path))
            # images = pdf2image.convert_from_bytes(file_data.read(), fmt="png", size=(1700, 2200),poppler_path=r"C:\Git\AutomationPOC\rest_api\poppler-0.68.0\bin")
            images = pdf2image.convert_from_bytes(file_data.read(), fmt="png", size=(1700, 2200))

            page_count = 1
            png_data = ''
            UPLOADS_DIR = os.path.dirname(__file__) + '/file_uploads/' + tenant + '/'
            for index, image in enumerate(images):
                image.save(f'{UPLOADS_DIR + str(id_file) + "/page_"}{index + 1}.png')
                if page_count > 1:
                    image = Image.open(f'{UPLOADS_DIR + str(id_file) + "/page_"}{index + 1}.png')
                    preprocessed_image = self.preprocess_image(
                        f'{UPLOADS_DIR + str(id_file) + "/page_"}{index + 1}.png')
                    if preprocessed_image is not None:
                        extracted_text = self.ocr_core(preprocessed_image)
                        if extracted_text:
                            png_data += extracted_text
                page_count = page_count + 1
            json_obj_2 = [{"template_name": "CIOMS"}, {"first_page_data": json_obj}, {"from_png_data": png_data},
                            {"from_second_page": from_second_page}, {"checkbox_data": checkbox_data}]
            f = open("temp_file_2.json", "w")
            f.write(json.dumps(json_obj_2))
            f.close()
            edited_file_name = "2.json"
            target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
            target_file_path = target_file_path + '/uploads/' + tenant + '/' + str(file_id) + "/" + edited_file_name
            s3 = boto3.client("s3",
                                region_name=settings.AWS_S3_REGION_NAME,
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

            s3.upload_file("temp_file_2.json", settings.AWS_STORAGE_BUCKET_NAME,
                            target_file_path)

        edited_file_name = (request.data.get('file_name').name).lower()
        target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
        target_file_path = target_file_path + '/uploads/' + tenant + '/' + str(file_id) + "/" + edited_file_name
        s3 = boto3.client("s3",
                            region_name=settings.AWS_S3_REGION_NAME,
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        s3.upload_file("temp_file.json", settings.AWS_STORAGE_BUCKET_NAME,
                        target_file_path)

        file_data = File.objects.using(tenant).get(id_file=file_id)
        file_data.is_data_extracted = 1
        file_data.save()

        response_data = {
            'message': "Extracted data saved successfully",
            'error': 0,
            'status_code': 200
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)
        # except Exception as exc:
        #     print(exc)
        #     return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)

    def preprocess_image(self, filename):
        """
        This function will handle the preprocessing of images using OpenCV.
        """
        try:
            img = cv2.imread(filename)
            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Apply thresholding
            _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            return binary_image
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None

    def ocr_core(self, image, custom_config=r'--oem 3 --psm 6'):
        """
        This function will handle the OCR processing of preprocessed images.
        """
        try:
            pil_img = Image.fromarray(image)
            data = pytesseract.image_to_data(pil_img, config=custom_config,
                                             output_type=pytesseract.Output.DICT)
            recognized_words = [word for word, conf in zip(data['text'], data['conf']) if
                                int(conf) > 0 and word.strip() != '']
            return ' '.join(recognized_words)
        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return None

    def s3_get_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

    def load_s3bucket_file(self, file_name):
        s3_client = self.s3_get_client()
        file = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                    Key=settings.AWS_PUBLIC_MEDIA_LOCATION + "/" + file_name)
        return file["Body"]
