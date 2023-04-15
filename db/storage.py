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


def check_if_object_exists_on_s3(bucket_name, object_key):
    """
    Check if an object exists in an S3 bucket
    :param s3: S3 client
    :param bucket_name: Bucket to check
    :param object_key: S3 object key
    :return: True if object exists, else False
    """

    try:
        _ = get_s3_client().head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise e


def upload_image_to_s3(bucket_key, object_key, image_data):
    """
    Uploads an image to S3.
    :param bucket_key: S3 bucket key
    :param object_key: S3 object key
    :param image_data: Image data
    :return: True if upload was successful, else False
    """
    try:
        _ = get_s3_client().put_object(
            Bucket=bucket_key,
            Key=object_key,
            Body=image_data,
            ContentType='image/jpeg')
    except ClientError as e:
        return False
    return True


def download_image_from_s3(bucket_key, object_key):
    """
    Downloads an image from S3.
    :param bucket_key: S3 bucket key
    :param object_key: S3 object key
    :return: Image data if download was successful, else None
    """
    try:
        response = get_s3_client().get_object(
            Bucket=bucket_key,
            Key=object_key)
    except ClientError as e:
        return None
    return response['Body'].read()


def delete_user_profile_image(image_url):
    """
    Deletes a user's profile image from S3.
    :param image_url: URL of the image
    """
    if not is_default_image(image_url) and not is_image_stored_in_s3(image_url):
        return

    get_s3_client().delete_object(
        Bucket='common-profile', Key=image_url.split('/')[-1])


def is_default_image(image_url):
    """
    Checks if a user's profile image is the default image.
    :param image_url: URL of the image
    :return: True if the image is the default image, else False
    """
    return image_url == 'common-profile.s3.us-west-1.amazonaws.com/profile_boy200.jpg'


def is_image_stored_in_s3(image_url):
    """
    Checks if a user's profile image is stored in S3.
    :param image_url: URL of the image
    :return: True if the image is stored in S3, else False
    """
    return image_url.startswith('https://common-profile.s3.us-west-1.amazonaws.com')
