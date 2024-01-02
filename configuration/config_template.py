class Config:
    # mode
    DEBUG= True

    # DATETIME_FORMAT
    DATETIME_FORMAT="%Y-%m-%d %H:%M:%I"

    # allowed host
    ALLOWED_HOSTS=[{{ALLOWED_HOSTS}}]
    CORS_ORIGIN_WHITELIST=[{{CORS_ORIGIN_WHITELIST}}]

    # db config values
    DATABASE_ENGINE='mysql_rds.backend'
    DATABASE_NAME= '{{DATABASE_NAME}}'
    DATABASE_HOST= '{{DATABASE_HOST}}'
    DATABASE_PORT= '3306'
    DATABASE_USER= '{{DATABASE_USER}}'
    DATABASE_PASSWORD= '{{DATABASE_PASSWORD}}'

    # aws config values
    AWS_STORAGE_BUCKET_NAME='{{AWS_STORAGE_BUCKET_NAME}}'
    AWS_ACCESS_KEY_ID = '{{AWS_ACCESS_KEY_ID}}'
    AWS_SECRET_ACCESS_KEY = '{{AWS_SECRET_ACCESS_KEY}}'
    AWS_S3_REGION_NAME = '{{AWS_S3_REGION_NAME}}'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_DEFAULT_ACL = None

    # third party config values
    CLIENT_ID = '{{CLIENT_ID}}'
    CLIENT_SECRET ='{{CLIENT_SECRET}}'
    ISSUER = '{{ISSUER}}'
    TOKEN_ENDPOINT = '{{TOKEN_ENDPOINT}}'
    REDIRECT_URI = '{{REDIRECT_URI}}'
    GRANT_TYPE = '{{GRANT_TYPE}}'
    PUBLICKEY_ENDPOINT = '{{PUBLICKEY_ENDPOINT}}'
	
	# the below 2 variables are used Auditlog app middle - for the Auditing purpose
    currrent_tenant_db='' 
    current_user_name=''
    current_case_id=''
    current_case_no=''
    current_case_ver=''

