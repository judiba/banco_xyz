# ============================================================
# TTYD — IAM Roles e Políticas
# 
# Papéis criados:
#   1. ttyd-agent-role      → AgentCore (PROD): acesso Bedrock + DynamoDB + Lambda + S3
#   2. ttyd-local-role      → Equipe LOCAL: assume role para testes com AWS real
#
# Política de mínimo privilégio seguindo o princípio LEVEL 18.
# ============================================================

# ── Data sources ──────────────────────────────────────────────
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
}


# ============================================================
# 1. IAM Role para o AgentCore (PROD)
# Assumida pelo serviço Amazon Bedrock AgentCore.
# ============================================================

resource "aws_iam_role" "agent_core_role" {
  name = "${var.project}-agent-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBedrockAgentCore"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_role_policy" "agent_core_policy" {
  name = "${var.project}-agent-policy-${var.environment}"
  role = aws_iam_role.agent_core_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [

      # ── Bedrock: Invocar modelo Claude ──────────────────────
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:Retrieve",
          "bedrock:RetrieveAndGenerate",
        ]
        Resource = "*"
      },

      # ── DynamoDB: Histórico de chat ──────────────────────────
      {
        Sid    = "DynamoDBChatHistory"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:DeleteItem",
          "dynamodb:BatchWriteItem",
        ]
        Resource = aws_dynamodb_table.chat_history.arn
      },

      # ── Lambda: Execução SQL no Redshift ────────────────────
      {
        Sid    = "LambdaRedshiftInvoke"
        Effect = "Allow"
        Action = ["lambda:InvokeFunction"]
        Resource = compact([
          var.redshift_lambda_arn_big_data,
          var.redshift_lambda_arn_id_unico,
        ])
      },

      # ── S3: Leitura de documentos RAG ───────────────────────
      {
        Sid    = "S3RAGRead"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
        ]
        Resource = var.rag_s3_bucket != "" ? [
          "arn:aws:s3:::${var.rag_s3_bucket}",
          "arn:aws:s3:::${var.rag_s3_bucket}/*",
        ] : ["arn:aws:s3:::placeholder-bucket"]
      },

      # ── Glue: Catálogo de dados T2SQL ───────────────────────
      {
        Sid    = "GlueCatalogRead"
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTables",
          "glue:GetTable",
        ]
        Resource = var.glue_database_name != "" ? [
          "arn:aws:glue:${local.region}:${local.account_id}:catalog",
          "arn:aws:glue:${local.region}:${local.account_id}:database/${var.glue_database_name}",
          "arn:aws:glue:${local.region}:${local.account_id}:table/${var.glue_database_name}/*",
        ] : ["arn:aws:glue:${local.region}:${local.account_id}:catalog"]
      },

      # ── CloudWatch: Logs do agente ───────────────────────────
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/bedrock/*"
      },
    ]
  })
}


# ============================================================
# 2. IAM Role para equipe LOCAL (times de desenvolvimento)
# Assumida por usuários autenticados via Entra ID (SAML).
# ============================================================

resource "aws_iam_role" "local_dev_role" {
  name = "${var.project}-local-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowSAMLFederation"
        Effect = "Allow"
        Principal = {
          # Em prod, substituir pelo ARN do Identity Provider do Entra ID
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "${var.project}-local-access"
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project
    Environment = "local"
    ManagedBy   = "terraform"
    Purpose     = "developer-access"
  }
}

resource "aws_iam_role_policy" "local_dev_policy" {
  name = "${var.project}-local-policy"
  role = aws_iam_role.local_dev_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [

      # Leitura e escrita no DynamoDB de chat (tabela de dev/local)
      {
        Sid    = "DynamoDBFullForLocal"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:DeleteItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:Scan",       # permitido só em local para debug
          "dynamodb:DescribeTable",
        ]
        Resource = aws_dynamodb_table.chat_history.arn
      },

      # Bedrock: invocar modelos para teste
      {
        Sid    = "BedrockLocalTest"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Resource = "*"
      },

      # Lambda Redshift: invocar para testes de SQL
      {
        Sid    = "LambdaRedshiftLocalTest"
        Effect = "Allow"
        Action = ["lambda:InvokeFunction"]
        Resource = compact([
          var.redshift_lambda_arn_big_data,
          var.redshift_lambda_arn_id_unico,
        ])
      },

      # S3: leitura de RAG
      {
        Sid    = "S3RAGReadLocal"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = var.rag_s3_bucket != "" ? [
          "arn:aws:s3:::${var.rag_s3_bucket}",
          "arn:aws:s3:::${var.rag_s3_bucket}/*",
        ] : ["arn:aws:s3:::placeholder-bucket"]
      },
    ]
  })
}


# ============================================================
# Outputs
# ============================================================

output "agent_core_role_arn" {
  description = "ARN da IAM Role do AgentCore (PROD) — use em AWS_EXTERNAL_ROLE_ARN"
  value       = aws_iam_role.agent_core_role.arn
}

output "local_dev_role_arn" {
  description = "ARN da IAM Role de desenvolvimento LOCAL"
  value       = aws_iam_role.local_dev_role.arn
}
