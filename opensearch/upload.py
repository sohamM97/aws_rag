import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = "soham-boto-s3-test"


def upload_file(file_name: str, bucket: str, object_name: Optional[str] = None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            file_name,
            bucket,
            object_name,
            ExtraArgs={"ACL": "public-read"},
        )
    except ClientError as e:
        logging.error(e)
        return None

    return f"https://{bucket}.s3.amazonaws.com/{object_name}"


if __name__ == "__main__":
    file_url = upload_file(
        file_name="hello.txt",
        bucket=BUCKET_NAME,
        object_name="testdir/hello.txt",
    )

    if file_url:
        print(f"File uploaded at {file_url}")
    else:
        print("Unable to upload file!")