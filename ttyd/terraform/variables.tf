# ============================================================
# TTYD — Terraform Variables
# Centraliza todas as variáveis configuráveis por ambiente.
# Use: terraform apply -var-file="dev.tfvars"
# ============================================================

variable "aws_region" {
  description = "Região AWS para todos os recursos"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Ambiente de execução: dev | local"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "local"], var.environment)
    error_message = "environment deve ser: dev ou local."
  }
}

variable "project" {
  description = "Nome do projeto (usado em tags e nomes de recursos)"
  type        = string
  default     = "ttyd"
}

# ── DynamoDB ──────────────────────────────────────────────────
variable "dynamodb_table_name" {
  description = "Nome da tabela DynamoDB para histórico de chat"
  type        = string
  default     = "ttyd-chat-history"
}

variable "dynamodb_ttl_seconds" {
  description = "TTL padrão das sessões em segundos (86400 = 24h)"
  type        = number
  default     = 86400
}

# ── Redshift Lambda ───────────────────────────────────────────
variable "redshift_lambda_arn_big_data" {
  description = "ARN da Lambda de execução SQL no Redshift (Lake Big Data)"
  type        = string
  default     = ""
}

variable "redshift_lambda_arn_id_unico" {
  description = "ARN da Lambda de execução SQL no Redshift (Lake ID Único)"
  type        = string
  default     = ""
}

# ── RAG / S3 ──────────────────────────────────────────────────
variable "rag_s3_bucket" {
  description = "Bucket S3 para documentos RAG"
  type        = string
  default     = ""
}

# ── AgentCore / Bedrock ───────────────────────────────────────
variable "bedrock_model_id" {
  description = "ID do modelo Bedrock (Claude)"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}

# ── ECR ───────────────────────────────────────────────────────
variable "ecr_repo_name" {
  description = "Nome do repositório ECR"
  type        = string
  default     = "ttyd-prod"
}

# ── Glue / T2SQL ──────────────────────────────────────────────
variable "glue_database_name" {
  description = "Nome do database no AWS Glue Catalog (T2SQL)"
  type        = string
  default     = ""
}
