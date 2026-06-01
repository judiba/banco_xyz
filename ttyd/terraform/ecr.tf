# ============================================================
# TTYD — ECR Repository
# (migrado do main.tf original para módulo dedicado)
# ============================================================

resource "aws_ecr_repository" "ttyd_repo" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

output "ecr_repository_url" {
  description = "URL do repositório ECR para push de imagens"
  value       = aws_ecr_repository.ttyd_repo.repository_url
}
