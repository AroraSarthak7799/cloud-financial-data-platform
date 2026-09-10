import os
from pathlib import Path

import boto3
from dotenv import load_dotenv


load_dotenv()


AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


RAW_FILES = {
    "customers": "data/raw/customers.csv",
    "dealers": "data/raw/dealers.csv",
    "vehicles": "data/raw/vehicles.csv",
    "loans": "data/raw/loans.csv",
    "payments": "data/raw/payments.csv",
}


def upload_raw_files() -> None:
    if not AWS_REGION:
        raise ValueError("AWS_REGION is not configured.")

    if not S3_BUCKET_NAME:
        raise ValueError("S3_BUCKET_NAME is not configured.")

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION,
    )

    for dataset_name, local_file in RAW_FILES.items():
        file_path = Path(local_file)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Raw file not found: {local_file}"
            )

        s3_key = (
            f"raw/{dataset_name}/{file_path.name}"
        )

        s3.upload_file(
            str(file_path),
            S3_BUCKET_NAME,
            s3_key,
        )

        print(
            f"Uploaded {local_file} "
            f"to s3://{S3_BUCKET_NAME}/{s3_key}"
        )


if __name__ == "__main__":
    upload_raw_files()