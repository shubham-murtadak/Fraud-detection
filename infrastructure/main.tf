provider "aws" {
  region = var.aws_region
}

# ==========================================
# 1. NETWORKING (VPC & SUBNETS)
# ==========================================
# We use the Default VPC to avoid massive boilerplate, but still get production networking!
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ==========================================
# 2. REGISTRY & MONITORING
# ==========================================
resource "aws_ecr_repository" "api_repo" {
  name                 = "fraudguard-api"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/ecs/fraudguard-api"
  retention_in_days = 30
}

# ==========================================
# 3. SECURITY GROUPS (FIREWALLS)
# ==========================================
# ALB Firewall: Allow ALL internet traffic on Port 80
resource "aws_security_group" "alb_sg" {
  name        = "fraudguard-alb-sg"
  description = "Allow inbound HTTP traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Firewall: ONLY allow traffic coming from the ALB!
resource "aws_security_group" "ecs_sg" {
  name        = "fraudguard-ecs-sg"
  description = "Allow inbound traffic from ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
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
}

# ==========================================
# 4. APPLICATION LOAD BALANCER (ALB)
# ==========================================
resource "aws_lb" "api_alb" {
  name               = "fraudguard-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "api_tg" {
  name        = "fraudguard-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/docs"
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }
}

resource "aws_lb_listener" "api_listener" {
  load_balancer_arn = aws_lb.api_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_tg.arn
  }
}

# ==========================================
# 5. COMPUTE & ORCHESTRATION (ECS & FARGATE)
# ==========================================
resource "aws_ecs_cluster" "main_cluster" {
  name = "fraudguard-cluster"
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "fraudguard_ecs_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# The Blueprint
resource "aws_ecs_task_definition" "api_task" {
  family                   = "fraudguard-api-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "fraudguard-container"
      image     = "${aws_ecr_repository.api_repo.repository_url}:latest"
      essential = true
      portMappings = [{ containerPort = 8000, hostPort = 8000 }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# The Daemon that keeps the containers running 24/7
resource "aws_ecs_service" "api_service" {
  name            = "fraudguard-service"
  cluster         = aws_ecs_cluster.main_cluster.id
  task_definition = aws_ecs_task_definition.api_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_tg.arn
    container_name   = "fraudguard-container"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.api_listener]
}
