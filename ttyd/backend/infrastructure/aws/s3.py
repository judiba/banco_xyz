import boto3
from pathlib import Path


class S3Storage:
    def __init__(self):
        self.client = boto3.client("s3")

    def download(self, bucket: str, key: str, target: str):
        Path(target).parent.mkdir(parents=True, exist_ok=True)

        self.client.download_file(
            bucket,
            key,
            target,
        )

    def upload(self, file_path: str, bucket: str, key: str):
        self.client.upload_file(
            file_path,
            bucket,
            key,
        )
