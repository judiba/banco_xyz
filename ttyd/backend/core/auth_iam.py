import boto3
import os

ROLE_ARN = os.getenv("AWS_EXTERNAL_ROLE_ARN")


def assume_external_role(session_name: str = "TTYDExternalSession"):
    """
    Assume a Role IAM para validar o acesso de usuários externos.
    Em um cenário real, isso geraria credenciais temporárias.
    """
    if not ROLE_ARN:
        return {"error": "AWS_EXTERNAL_ROLE_ARN não configurada"}

    sts_client = boto3.client("sts")

    try:
        assumed_role = sts_client.assume_role(RoleArn=ROLE_ARN, RoleSessionName=session_name)
        return {
            "status": "authenticated",
            "user": assumed_role["AssumedRoleUser"]["Arn"],
            "credentials": assumed_role["Credentials"],
        }
    except Exception as e:
        return {"error": str(e)}
