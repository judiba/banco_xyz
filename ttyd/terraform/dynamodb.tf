# ============================================================
# TTYD — DynamoDB: Histórico de Chat
# Diagrama: "Memória de chat & Sugestões — DynamoDB"
# ============================================================

resource "aws_dynamodb_table" "chat_history" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"   # serverless — sem capacity planning
  hash_key     = "session_id"
  range_key    = "timestamp"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # TTL automático — exclui sessões antigas sem custo extra
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Ponto-em-tempo para recuperação de dados (PROD)
  point_in_time_recovery {
    enabled = var.environment == "prod"
  }

  # Criptografia em repouso com chave gerenciada pela AWS
  server_side_encryption {
    enabled = true
  }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Component   = "memory"
  }
}

output "dynamodb_table_name" {
  description = "Nome da tabela DynamoDB de histórico de chat"
  value       = aws_dynamodb_table.chat_history.name
}

output "dynamodb_table_arn" {
  description = "ARN da tabela DynamoDB"
  value       = aws_dynamodb_table.chat_history.arn
}
