# infra variables for AWS

variable "region" {
    description = "region for aws resources"
    type = string
    default = "eu-west-2"
}

variable "account_id" {
  description = "aws account id"
  type = string
}

variable "ecr_uri" {
  description = "URI for ECR image"
  type = string
}

variable "app_name" {
  description = "bat or brolly app name"
  type = string
  default = "bat-or-brolly"
}

# environment can be dev, staging or prod - dev is always default first
variable "environment" {
  description = "environment for code"
  type = string
  default = "dev"
}

variable "container_port" {
  description = "port to connect to container"
  type = number
  default = 8000
}

variable "desired_task_count" {
  description = "desired number of tasks running"
  type = number
  default = 1
}

variable "cpu" {
  description = "cpu for each task"
  type = number
  default = 256
}

variable "memory" {
  description = "memory allocated to each task"
  type = number
  default = 512
}
