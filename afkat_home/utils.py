import boto3
import json
from django.conf import settings


def get_available_themes():
    """
    Fetch available themes from the S3 bucket.
    Returns a dictionary of theme_name: theme_url pairs.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
        region_name = settings.AWS_S3_REGION_NAME
    )

    themes = {}
    prefix = 'default_images/default_patterns/'

    try:
        response = s3_client.list_objects_v2(
            Bucket = settings.AWS_STORAGE_BUCKET_NAME,
            Prefix = prefix
        )

        if 'Contents' in response:
            for item in response['Contents']:
                if item['Key'] == prefix:
                    continue

                file_name = item['Key'].split('/')[-1]
                theme_name = file_name.split('.')[0]

                theme_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{item['Key']}"
                themes[theme_name] = theme_url

        return themes
    except Exception as e:
        print(f"Error fetching themes from S3: {e}")
        return {}
