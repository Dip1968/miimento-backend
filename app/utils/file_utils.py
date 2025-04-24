from io import BytesIO
import os
import shutil
import time
import requests

from fastapi import UploadFile

from app.config import get_config
from app.core.constants.generic_constants import FileAttachmentType
from app.utils.s3_utils import delete_file_from_s3, get_file_from_s3, upload_file_to_s3

config = get_config()  # Assuming a function to get the configuration


def upload_file_util(file, tenant=None):
    storage_type = config.FILE_STORAGE_TYPE

    if storage_type == FileAttachmentType.Local:
        return upload_to_local_storage(file)
    if storage_type == FileAttachmentType.UPLOAD_CARE:
        # Upload logic for uploadCare storage
        # Example: upload_to_uploadcare(file)
        pass
    elif storage_type == FileAttachmentType.S3:
        # Upload logic for S3 storage
        return upload_file_to_s3(file, tenant)


def get_file_util(filename, tenant=None):
    storage_type = config.FILE_STORAGE_TYPE

    if storage_type == FileAttachmentType.Local:
        return get_file_from_local_storage(filename)

    if storage_type == FileAttachmentType.UPLOAD_CARE:
        # Fetch logic for uploadCare storage
        # Example: return fetch_from_uploadcare(filename)
        pass
    elif storage_type == FileAttachmentType.S3:
        # Fetch logic for S3 storage
        return get_file_from_s3(filename, tenant)
    else:
        raise ValueError("Unsupported storage type")

    # Return file info
    return {"file_name": filename, "storage_type": storage_type}


def get_file_attachment_in_memory_util(filename, tenant=None):
    storage_type = config.FILE_STORAGE_TYPE

    if storage_type == FileAttachmentType.Local:
        file_path = get_file_from_local_storage(filename)
        with open(file_path, "rb") as file:
            file_in_memory = BytesIO(file.read())
            file_in_memory.name = filename

        return file_in_memory

    if storage_type == FileAttachmentType.UPLOAD_CARE:
        # Fetch logic for uploadCare storage
        # Example: return fetch_from_uploadcare(filename)
        pass
    elif storage_type == FileAttachmentType.S3:
        # Fetch logic for S3 storage
        url = get_file_from_s3(filename, tenant)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        file_in_memory = BytesIO(response.content)
        file_in_memory.name = filename
        return file_in_memory
    else:
        raise ValueError("Unsupported storage type")

    # Return file info
    return {"file_name": filename, "storage_type": storage_type}


def upload_to_local_storage(file: UploadFile, local_storage_path: str = "tmp/"):
    # Create the directory if it doesn't exist
    os.makedirs(local_storage_path, exist_ok=True)

    # Get the current Unix timestamp
    timestamp = int(time.time())

    # Split the filename and the extension
    file_name, file_extension = os.path.splitext(file.filename)

    new_file_name = f"{file_name}_{timestamp}{file_extension}"
    file_props = {
        "name": file.filename,
        "size": file.size,
        "type": file.headers["content-type"],
        "unique_filename": new_file_name,
    }

    # Define the full path for the new file
    file_path = os.path.join(local_storage_path, new_file_name)

    # copy file contents
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file.file.close()

    return file_props


def get_file_from_local_storage(filename: str, local_storage_path: str = "tmp/"):
    file_path = os.path.join(local_storage_path, filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found in local storage.")

    return file_path


def delete_file(filename, tenant=None):
    storage_type = config.FILE_STORAGE_TYPE
    if storage_type == FileAttachmentType.Local:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    if storage_type == FileAttachmentType.S3:
        # Logic to delete file from S3 storage
        return delete_file_from_s3(filename, tenant)
    return False
