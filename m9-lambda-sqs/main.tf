terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.3.0"
}

provider "aws" {
  region  = var.region
}

module "iam" {
  source  = "./modules/iam"
  prefix  = var.prefix
  sqs_arn = module.sqs.queue_arn
}


module "sqs" {
  source = "./modules/sqs"
  prefix = var.prefix
}


module "lambda" {
  source   = "./modules/lambda"
  prefix   = var.prefix
  role_arn = module.iam.role_arn
  sqs_arn  = module.sqs.queue_arn
}