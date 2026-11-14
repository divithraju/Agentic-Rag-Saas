# Skeleton: AWS deployment (ECS Fargate API + RDS Postgres/pgvector + S3 ingestion bucket + ALB).
# Extend into modules (network, data, compute) as you build. On-prem path: see docs/ARCHITECTURE.md (k3s + Lustre/NFS + vLLM).
terraform {
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = var.region }
variable "region" { default = "ap-south-1" }
variable "project" { default = "agentic-rag-saas" }

resource "aws_s3_bucket" "ingest" { bucket = "${var.project}-ingest-${data.aws_caller_identity.me.account_id}" }
data "aws_caller_identity" "me" {}

# TODO: aws_db_instance (postgres 16 + pgvector), aws_ecs_cluster/service, aws_lb, aws_secretsmanager_secret (API keys)
