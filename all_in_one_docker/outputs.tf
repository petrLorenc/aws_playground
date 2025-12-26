output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = var.create_elastic_ip ? aws_eip.app[0].public_ip : aws_instance.app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.app.public_dns
}

output "elastic_ip" {
  description = "Elastic IP address (if created)"
  value       = var.create_elastic_ip ? aws_eip.app[0].public_ip : null
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.app.id
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.app.name
}

output "secrets_manager_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.app.arn
}

output "ssm_connect_command" {
  description = "Command to connect to the instance via SSM"
  value       = "aws ssm start-session --target ${aws_instance.app.id}"
}

output "application_url" {
  description = "Application URL"
  value       = var.create_route53_record && var.domain_name != "" ? "http://${var.domain_name}" : "http://${var.create_elastic_ip ? aws_eip.app[0].public_ip : aws_instance.app.public_ip}"
}
