import gzip
import tarfile
import io
import os
from boto3 import client, resource
from rest_framework.views import APIView
from data_ingestion import settings


class S3Bucket(APIView):
    def s3_get_client(self):
        return client(
            's3', 
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
    
    def s3_get_resource(self):
        return resource(
            's3', 
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

    def upload_to_s3(self, target_folder, file_name, file):
        target_file_path = settings.AWS_PUBLIC_MEDIA_LOCATION
        target_file_path = target_file_path + target_folder + "/" + file_name
        s3_resource = self.s3_get_resource()
        s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(
            Key=target_file_path,
            Body=file)

    def load_s3bucket_file(self, file_name):
        s3_client = self.s3_get_client()
        print(settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_name)
        file = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_name)
        print(file)
        return file["Body"]

    # def delete_s3bucket_file(self, file_name):
    #     s3_client = self.s3_get_client()
    #     response = s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_name)
    #     return response

    def upload_file_to_s3bucket(self, file_name, file_url):
        s3_client = self.s3_get_client()
        response = s3_client.upload_file(file_url, settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_name)
        return response

    def unzip_file(self, file_src_name, file_target_name):
        s3_client = self.s3_get_client()
        # response = s3_client.upload_fileobj(
        #     Fileobj=gzip.GzipFile(                                                    # read in the output of gzip -d
        #         None,                                                                 # just return output as BytesIO
        #         'rb',                                                                 # read binary
        #         fileobj=io.BytesIO(s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_src_name)['Body'].read())
        #     ),
        #     Bucket=settings.AWS_STORAGE_BUCKET_NAME,                                   # target bucket, writing to
        #     Key=settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_target_name+"/")               # target key, writing to
        # return response
        input_tar_content = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=settings.AWS_PUBLIC_MEDIA_LOCATION+"/"+file_src_name)['Body'].read()
        uncompressed_key="{}/{}/".format(settings.AWS_PUBLIC_MEDIA_LOCATION,file_target_name)
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        with tarfile.open(fileobj = io.BytesIO(input_tar_content)) as tar:
            for file in tar:
                if (file.isfile()):
                    inner_file_bytes = tar.extractfile(file).read()
                    file_loc = os.path.join(uncompressed_key,(file.name).split("./")[1])
                    s3_client.upload_fileobj(io.BytesIO(inner_file_bytes), Bucket=bucket,Key=file_loc)
            tar.close()              
        return True

    def generate_presigned_url(self, file_url):
        s3_client = self.s3_get_client()
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['Authorization'],
                'AllowedMethods': ['GET', 'PUT'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag', 'x-amz-request-id'],
                'MaxAgeSeconds': 3000
            }]
        }
        s3_client.put_bucket_cors(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            CORSConfiguration=cors_configuration)
        s3_path = os.path.join(settings.AWS_PUBLIC_MEDIA_LOCATION, file_url)
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_path},
            ExpiresIn=1296000,  # 30 days
            HttpMethod='GET'
        )

    def list_objects_from_directory(self, directory):
        s3_client = self.s3_get_client()
        response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix="{}/{}".format(settings.AWS_PUBLIC_MEDIA_LOCATION, directory))
        files = response.get("Contents")
        return files

    def get_s3_object(self, key):
        s3_resource = self.s3_get_resource()
        object = s3_resource.Object(settings.AWS_STORAGE_BUCKET_NAME, "{}/{}".format(settings.AWS_PUBLIC_MEDIA_LOCATION, key))
        return object.get()['Body']
