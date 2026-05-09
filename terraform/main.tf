terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "bat-or-brolly-terraform-state"
    key            = "bat-or-brolly/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "bat-or-brolly-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

# Data Source = data.type.name.attribute

# VPC
data "aws_vpc" "default" {
  default = true
}

# Subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Resources

# ECR
resource "aws_ecr_repository" "app_container" {
  name                 = "${var.app_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# CloudWatch Logs
resource "aws_cloudwatch_log_group" "logs" {
  # /ecs/app-name-environment
  name              = "/ecs/${var.app_name}-${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# IAM

# Which role to Assume
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

#Role
resource "aws_iam_role" "role" {
  name               = "${var.app_name}-${var.environment}-execution-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }

}

# Policy

resource "aws_iam_role_policy_attachment" "policy" {
  # role comes from the resource defined above
    role       = aws_iam_role.role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# Security Groups

# ALB Security Group


# ECS SG
resource "aws_security_group" "ecs_sg" {
  name        = "${var.app_name}-${var.environment}-ecs-sg"
  description = "Allow traffic from ALB to ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "ECS task security group for Bat or Brolly"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}


# ECS
# Cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "${var.app_name}-${var.environment}-ecs-cluster"

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "ecs_task" {
  family = "${var.app_name}-${var.environment}"

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.role.arn
  container_definitions = jsonencode([
    {
      name      = aws_ecr_repository.app_container.name
      image     = var.ecr_uri
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.logs.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ECS Service
resource "aws_ecs_service" "ecs_service" {
  name            = "${var.app_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task.arn
  desired_count   = var.desired_task_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.alb_tg.arn
    container_name   = aws_ecr_repository.app_container.name
    container_port   = var.container_port
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

