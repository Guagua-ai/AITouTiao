import os
import boto3
from botocore.exceptions import ClientError

def get_s3_client():
    """
    Returns an S3 client.
    """
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    return boto3.client('s3', 
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_access_key)


def check_if_object_exists(s3, bucket_name, object_key):
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e