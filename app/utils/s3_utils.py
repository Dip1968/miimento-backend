import os
import time
from app.adapter.aws_adapter import get_s3_conn
from app.config import get_config

config = get_config()


def upload_file_to_s3(file, tenant):
    # Get S3 client
    s3 = get_s3_conn()

    # Generate a unique file name by appending the current Unix timestamp
    timestamp = int(time.time())
    file_name, file_extension = os.path.splitext(file.filename)
    object_name = f"{file_name}_{timestamp}{file_extension}"

    # Upload the file
    s3.upload_fileobj(
        file.file,
        config.AWS_ATTACHMENT_BUCKET_NAME,
        f"{config.ENV}/{tenant.get("tenant_url_code","tmp")}/{object_name}",
        {"StorageClass": "INTELLIGENT_TIERING", "ContentType": file.headers["content-type"]},
    )

    file_resp = {
        "name": file.filename,
        "size": file.size,
        "type": file.headers["content-type"],
        "unique_filename": object_name,
    }
    return file_resp


def get_file_from_s3(file_name, tenant):
    # Get S3 client
    s3 = get_s3_conn()

    # Generate a pre-signed URL for the uploaded file
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": config.AWS_ATTACHMENT_BUCKET_NAME,
            "Key": f"{config.ENV}/{tenant.get("tenant_url_code","tmp")}/{file_name}",
        },
        ExpiresIn=3600,
    )
    return url


def delete_file_from_s3(file_name, tenant):
    # Get S3 client
    s3 = get_s3_conn()

    # Delete the file from S3
    s3.delete_object(
        Bucket=config.AWS_ATTACHMENT_BUCKET_NAME,
        Key=f"{config.ENV}/{tenant.get("tenant_url_code","tmp")}/{file_name}",
    )
    return True
