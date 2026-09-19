output "ecr_repository_url" {
  description = "The URL of the Amazon ECR Repository"
  value       = aws_ecr_repository.api_repo.repository_url
}

output "cloudwatch_log_group" {
  description = "The name of the CloudWatch Log Group for monitoring"
  value       = aws_cloudwatch_log_group.api_logs.name
}

output "ecs_cluster_name" {
  description = "The name of the ECS Cluster"
  value       = aws_ecs_cluster.main_cluster.name
}
