# ============================================================
# TTYD — AWS Secrets Manager
# Cria o secret "ttyd/{env}/config" com placeholder.
# Preencher os valores reais via Console ou CLI após o apply.
# ============================================================

resource "aws_secretsmanager_secret" "ttyd_config" {
  name        = "ttyd/${var.environment}/config"
  description = "Configurações sensíveis do TTYD (${var.environment})"

  # Rotação automática — desabilitada por padrão, habilitar em PROD
  # rotation_rules { automatically_after_days = 30 }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Component   = "secrets"
  }
}

# Versão inicial do secret com chaves vazias (placeholder)
# ⚠️  Preencher valores reais via: aws secretsmanager put-secret-value
resource "aws_secretsmanager_secret_version" "ttyd_config_initial" {
  secret_id = aws_secretsmanager_secret.ttyd_config.id

  secret_string = jsonencode({
    REDSHIFT_LAMBDA_ARN          = var.redshift_lambda_arn_big_data
    REDSHIFT_LAKE_BIG_DATA_ARN   = var.redshift_lambda_arn_big_data
    REDSHIFT_LAKE_ID_UNICO_ARN   = var.redshift_lambda_arn_id_unico
    RAG_BUCKET                   = var.rag_s3_bucket
    GLUE_DATABASE                = var.glue_database_name
  })

  # Ignora mudanças manuais nos valores (evita sobrescrever com terraform apply)
  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Política: permite que a IAM Role do AgentCore leia o secret
resource "aws_secretsmanager_secret_policy" "ttyd_config_policy" {
  secret_arn = aws_secretsmanager_secret.ttyd_config.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AgentCoreReadSecret"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.agent_core_role.arn
        }
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.ttyd_config.arn
      },
      {
        Sid    = "LocalDevReadSecret"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.local_dev_role.arn
        }
        Action   = ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"]
        Resource = aws_secretsmanager_secret.ttyd_config.arn
      }
    ]
  })
}

output "secret_arn" {
  description = "ARN do secret TTYD no Secrets Manager"
  value       = aws_secretsmanager_secret.ttyd_config.arn
}

output "secret_name" {
  description = "Nome do secret (use em scripts de deploy)"
  value       = aws_secretsmanager_secret.ttyd_config.name
}
