class Config:
    # mode
    DEBUG = True

    # DATETIME_FORMAT
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%I"

    # allowed host
    ALLOWED_HOSTS = ['*']
    CORS_ORIGIN_WHITELIST = ["https://localhost:4200", "https://localhost:3000"]

    # db config values
    DATABASE_ENGINE = 'django.db.backends.mysql'
    DATABASE_NAME = 'data_ingestion'
    DATABASE_HOST = 'localhost'
    DATABASE_PORT = '3306'
    DATABASE_USER = 'root'
    DATABASE_PASSWORD = 'Password@123'

    # aws config values
    AWS_STORAGE_BUCKET_NAME = 'ingest-new'
    AWS_ACCESS_KEY_ID = 'AKIAZDWTMXTK6AOP2ENE'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_S3_REGION_NAME = 'eu-north-1'
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_DEFAULT_ACL = None

    # third party config values
    CLIENT_ID = '9124e5c3-0bb4-4370-8fd9-732abdcab9c9'
    CLIENT_SECRET = 'PJ9q6ycPa5Bdi1hinmYsgF4VB4-o2jfcf4our4N8'
    ISSUER = "qinfs.qinecsa.com"
    TOKEN_ENDPOINT = "/adfs/oauth2/token"
    REDIRECT_URI = 'https://localhost:4200'
    GRANT_TYPE = 'password'
    PUBLICKEY_ENDPOINT = '/adfs/discovery/keys'
    currrent_tenant_db = ''
    current_user_name = ''

    # the below 2 variables are used Auditlog app middle - for the Auditing purpose
    currrent_tenant_db = ''
    current_user_name = ''
    current_case_id = ''
    current_case_no = ''
    current_case_ver = ''

