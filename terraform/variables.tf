variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "project_name" {
  type    = string
  default = "network-monitoring"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "eks_cluster_version" {
  type    = string
  default = "1.29"
}

variable "db_username" {
  type    = string
  default = "nmadmin"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "ChangeMeInProduction123!"
}
