output "vpc_id" {
  value = aws_vpc.main.id
}

output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "s3_logs_bucket" {
  value = aws_s3_bucket.logs.bucket
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "cloudwatch_app_log_group" {
  value = aws_cloudwatch_log_group.app.name
}
