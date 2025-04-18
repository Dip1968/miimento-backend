import boto3

from app.config import get_config

config = get_config()

# Create a single AWS instance and reuse it
aws_session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION_NAME,
)


def get_s3_conn():
    # Create an S3 client
    return aws_session.client("s3")
