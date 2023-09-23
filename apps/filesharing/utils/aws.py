import boto3
import filesec.settings as settings

# Initializing a session
session = boto3.Session(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# reusable clients 

s3_client = session.client('s3')
cloudfront = session.client('cloudfront')