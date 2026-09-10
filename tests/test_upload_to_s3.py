import pytest

import src.upload_to_s3 as upload_to_s3


class FakeS3Client:
    def __init__(self):
        self.uploads = []

    def upload_file(self, filename, bucket, key):
        self.uploads.append((filename, bucket, key))


def test_upload_raw_files_uploads_expected_files(tmp_path, monkeypatch):
    customers_file = tmp_path / "customers.csv"
    dealers_file = tmp_path / "dealers.csv"

    customers_file.write_text("customer_id\nCUST00001\n")
    dealers_file.write_text("dealer_id\nDLR0001\n")

    monkeypatch.setattr(
        upload_to_s3,
        "AWS_REGION",
        "ca-central-1",
    )

    monkeypatch.setattr(
        upload_to_s3,
        "S3_BUCKET_NAME",
        "test-bucket",
    )

    monkeypatch.setattr(
        upload_to_s3,
        "RAW_FILES",
        {
            "customers": str(customers_file),
            "dealers": str(dealers_file),
        },
    )

    fake_s3 = FakeS3Client()

    monkeypatch.setattr(
        upload_to_s3.boto3,
        "client",
        lambda service_name, region_name: fake_s3,
    )

    upload_to_s3.upload_raw_files()

    assert fake_s3.uploads == [
        (
            str(customers_file),
            "test-bucket",
            "raw/customers/customers.csv",
        ),
        (
            str(dealers_file),
            "test-bucket",
            "raw/dealers/dealers.csv",
        ),
    ]


def test_upload_raw_files_rejects_missing_file(tmp_path, monkeypatch):
    missing_file = tmp_path / "missing.csv"

    monkeypatch.setattr(
        upload_to_s3,
        "AWS_REGION",
        "ca-central-1",
    )

    monkeypatch.setattr(
        upload_to_s3,
        "S3_BUCKET_NAME",
        "test-bucket",
    )

    monkeypatch.setattr(
        upload_to_s3,
        "RAW_FILES",
        {
            "customers": str(missing_file),
        },
    )

    fake_s3 = FakeS3Client()

    monkeypatch.setattr(
        upload_to_s3.boto3,
        "client",
        lambda service_name, region_name: fake_s3,
    )

    with pytest.raises(
        FileNotFoundError,
        match="Raw file not found",
    ):
        upload_to_s3.upload_raw_files()


def test_upload_raw_files_requires_region(monkeypatch):
    monkeypatch.setattr(
        upload_to_s3,
        "AWS_REGION",
        None,
    )

    monkeypatch.setattr(
        upload_to_s3,
        "S3_BUCKET_NAME",
        "test-bucket",
    )

    with pytest.raises(
        ValueError,
        match="AWS_REGION is not configured",
    ):
        upload_to_s3.upload_raw_files()