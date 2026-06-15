resource "aws_cloudwatch_log_group" "app" {
  name              = "/network-monitoring/${var.environment}/app"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "eks" {
  name              = "/network-monitoring/${var.environment}/eks"
  retention_in_days = 14
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project_name}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EKS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "EKS node CPU high"
  treat_missing_data  = "notBreaching"
}
