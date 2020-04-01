import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes
import json

def lambda_handler(event, context):
    # TODO implement
    
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:172810175626:deployPortfolio')
    
    location = {
        "bucketName": 'portfoliobuild.xxxxxxxxx.com',
        "objectKey": 'portfolio_zip'
    }
    
    try:
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]
                    
        #Config is for server side encryption in S3
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        portfolio_bucket = s3.Bucket('portfolio.xxxxxxxxxxx.com')
        build_bucket = s3.Bucket(location["bucketName"])
        
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
        
        print("Building Portfolio from " + str(location))
        
        with zipfile.ZipFile(portfolio_zip, mode='r') as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
    
                content_type = mimetypes.guess_type(nm)[0]
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': content_type, 'ACL': "public-read" })
    
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId = job["id"])
    except:
        topic.publish(Subject="Portfolio Deploy Failed", Message="The Portfolio was not deployed successfully!")
        raise
    
    return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
