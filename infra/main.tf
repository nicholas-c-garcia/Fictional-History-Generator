terraform {
  required_providers {
    aws = {
      version = ">= 4.0.0"
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
  access_key = "AKIA37AAJ3IXT4Z6NN6K"
  secret_key = "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"
}

#S3 Bucket
resource "aws_s3_bucket" "lambda" {}

#Locals block is used to declare constants that 
# you can use throughout your code
locals {
  create_obituary = "create-obituary-30153409"
  get_obituaries  = "get-obituaries-30153409"

  handler_name  = "main.handler"

  artifact_create = "artifact-create.zip"         #might have to change this part
  artifact_get = "artifact-get.zip"
}

#Zips main.py for each function 
data "archive_file" "zip_create" {
  type = "zip"
  #source_file = "../functions/create-obituary/main.py"
  source_dir = "../functions/create-obituary"
  output_path = local.artifact_create
}
data "archive_file" "zip_get" {
  type = "zip"
  source_file = "../functions/get-obituaries/main.py"
  output_path = local.artifact_get
}

#IAM role for Lambda functions
resource "aws_iam_role" "lambda" {
  name               = "iam-for-lambda-obituaries"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# create a policy for publishing logs to CloudWatch
resource "aws_iam_policy" "logs" {
  name        = "lambda-logging-obituaries"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "polly:SynthesizeSpeech",
        "lambda:*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "states:StartExecution",
        "states:DescribeExecution",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath",
        "s3:*"
      ],
      "Resource": [
        "*",
        "arn:aws:dynamodb:*:*:table/*",
        "arn:aws:ssm:ca-central-1:822486882863:parameter/*",
        "arn:aws:logs:*:*:*"
      ],
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.logs.arn
}

#Lambda Functions
resource "aws_lambda_function" "lambda_create" {
  role = aws_iam_role.lambda.arn
  filename = local.artifact_create
  function_name = local.create_obituary
  handler = local.handler_name
  source_code_hash = data.archive_file.zip_create.output_base64sha256

  runtime = "python3.9"
}
resource "aws_lambda_function" "lambda_get" {
  role = aws_iam_role.lambda.arn
  filename = local.artifact_get
  function_name = local.get_obituaries
  handler = local.handler_name
  source_code_hash = data.archive_file.zip_get.output_base64sha256

  runtime = "python3.9"
}

#Lambda URLs
resource "aws_lambda_function_url" "url_create" {
  function_name      = aws_lambda_function.lambda_create.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

resource "aws_lambda_function_url" "url_get" {
  function_name      = aws_lambda_function.lambda_get.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET"]
    allow_headers     = ["*"]
    expose_headers    = ["keep-alive", "date"]
  }
}

#DynamoDB Table
resource "aws_dynamodb_table" "obituaries-30143076" {
  name         = "obituaries-30143076"
  billing_mode = "PROVISIONED"
  read_capacity = 1
  write_capacity = 1

  hash_key = "stupidID"          # Partition key (1)
  range_key = "id"               # Sort Key (UUIDv4)

  #Different cells on table
  #id
  attribute {
    name = "id"
    type = "S"
  }
    attribute {
    name = "stupidID"
    type = "S"
  }


}

#Output
# output the name of the bucket after creation
output "lambda_url_create_output" {
  value = aws_lambda_function_url.url_create.function_url
}
output "lambda_url_get_output" {
  value = aws_lambda_function_url.url_get.function_url
}
output "obituaries_bucket" {
  value = aws_s3_bucket.lambda.bucket
}

# two lambda functions w/ function url
# one dynamodb table
# roles and policies as needed
# step functions (if you're going for the bonus marks)
