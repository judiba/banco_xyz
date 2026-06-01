import os


def get_document_loader():
    provider = os.getenv("INFRA_PROVIDER", "aws")

    if provider == "aws":
        from infrastructure.providers.aws.s3_document_loader import (
            S3DocumentLoader,
        )
        import boto3

        return S3DocumentLoader(boto3.client("s3"))

    raise RuntimeError("Provider not supported")
