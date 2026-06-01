#!/usr/bin/env python3
"""Cria tabelas DynamoDB para a API v1 TTYD."""

import argparse
import os
import sys

import boto3

PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "ttyd")
REGION = os.getenv("AWS_REGION", "us-east-1")
ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")


def _client():
    kwargs = {"region_name": REGION}
    if ENDPOINT:
        kwargs["endpoint_url"] = ENDPOINT
    return boto3.client("dynamodb", **kwargs)


def _create_if_not_exists(client, definition: dict) -> None:
    name = definition["TableName"]
    try:
        client.describe_table(TableName=name)
        print(f"✓ Tabela já existe: {name}")
    except client.exceptions.ResourceNotFoundException:
        client.create_table(**definition)
        print(f"+ Tabela criada: {name}")
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria tabelas DynamoDB TTYD")
    parser.add_argument("--prefix", default=PREFIX)
    args = parser.parse_args()
    prefix = args.prefix
    client = _client()

    tables = [
        {
            "TableName": f"{prefix}-users",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "username", "AttributeType": "S"},
                {"AttributeName": "adOid", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "username-index",
                    "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
                {
                    "IndexName": "adOid-index",
                    "KeySchema": [{"AttributeName": "adOid", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
        {
            "TableName": f"{prefix}-folders",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "userId", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "userId-index",
                    "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
        {
            "TableName": f"{prefix}-conversations",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "lastUpdatedAt", "AttributeType": "N"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "userId-lastUpdatedAt-index",
                    "KeySchema": [
                        {"AttributeName": "userId", "KeyType": "HASH"},
                        {"AttributeName": "lastUpdatedAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
        {
            "TableName": f"{prefix}-messages",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "conversationId", "AttributeType": "S"},
                {"AttributeName": "createdAt", "AttributeType": "N"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "conversationId-createdAt-index",
                    "KeySchema": [
                        {"AttributeName": "conversationId", "KeyType": "HASH"},
                        {"AttributeName": "createdAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
        {
            "TableName": f"{prefix}-refresh-tokens",
            "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        },
    ]

    for table in tables:
        _create_if_not_exists(client, table)

    print("\nTabelas prontas. Exemplo local:")
    print("  DYNAMODB_ENDPOINT=http://localhost:8001 python scripts/create_dynamodb_tables.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
