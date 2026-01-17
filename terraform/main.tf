
resource "random_integer" "suffix" { min = 10000 max = 99999 }

resource "aws_s3_bucket" "bucket" {
  bucket = "${var.project_tag}-bucket-${random_integer.suffix.result}"
  tags = { Project = var.project_tag }
}

resource "aws_security_group" "sg" {
  name = "${var.project_tag}-sg"
  ingress = [for p in [22,80,8080,8501,9092,5432] : {
    description = "port"
    from_port = p
    to_port   = p
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
  }]
  egress = [{
    description = "all"
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = []
    prefix_list_ids = []
    security_groups = []
    self = false
  }]
}

data "aws_ami" "al2" {
  owners      = ["amazon"]
  most_recent = true
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_iam_role" "ec2_role" {
  name = "${var.project_tag}-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "s3_access" {
  name = "${var.project_tag}-s3-policy"
  role = aws_iam_role.ec2_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = ["s3:*"],
      Resource = "*"
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_tag}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_instance" "vm" {
  ami                  = data.aws_ami.al2.id
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  key_name             = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.sg.id]
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              amazon-linux-extras install docker -y
              systemctl enable docker
              systemctl start docker
              curl -L "https://github.com/docker/compose/releases/download/2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              EOF
  tags = { Project = var.project_tag }
}

output "bucket_name" { value = aws_s3_bucket.bucket.bucket }
output "public_ip"   { value = aws_instance.vm.public_ip }
