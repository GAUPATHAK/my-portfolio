import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes
import json

def lambda_handler(event, context):
    # TODO implement

    #aws_profile = "xxxxxx"
    #session = boto3.Session(profile_name=aws_profile)
    #s3 = session.resource('s3', config=Config(signature_version='s3v4'))

    #Config is for server side encryption in S3
    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    
    portfolio_bucket = s3.Bucket('portfolio.xxxxxxxxxxxx.com')
    build_bucket = s3.Bucket('portfoliobuild.xxxxxxxxxxx.com')
    
    portfolio_zip = io.BytesIO()
    build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
    
    with zipfile.ZipFile(portfolio_zip, mode='r') as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)

            content_type = mimetypes.guess_type(nm)[0]
            #upload_fileobj works with io obj only in python v3.8.*
            portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': content_type, 'ACL': "public-read" })
            
    return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
