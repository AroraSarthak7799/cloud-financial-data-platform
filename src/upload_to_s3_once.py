import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from upload_to_s3 import RAW_FILES


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def upload_if_missing():
    region = os.getenv("AWS_REGION")
    bucket = os.getenv("S3_BUCKET_NAME")

    if not region or not bucket:
        raise ValueError("AWS_REGION or S3_BUCKET_NAME is missing")

    s3 = boto3.client("s3", region_name=region)

    # Check all local files before starting uploads.
    for relative_path in RAW_FILES.values():
        if not (PROJECT_ROOT / relative_path).is_file():
            raise FileNotFoundError(relative_path)

    for dataset, relative_path in RAW_FILES.items():
        path = PROJECT_ROOT / relative_path
        key = f"raw/{dataset}/{path.name}"

        try:
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=path.read_bytes(),
                ContentType="text/csv",
                IfNoneMatch="*",
            )
            print(f"Uploaded: {key}")

        except ClientError as error:
            code = error.response.get("Error", {}).get("Code")

            if code in ("PreconditionFailed", "412"):
                print(f"Already exists, skipped: {key}")
            else:
                raise


if __name__ == "__main__":
    upload_if_missing()