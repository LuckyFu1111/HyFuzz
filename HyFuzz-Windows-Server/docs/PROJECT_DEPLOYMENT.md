# HyFuzz Deployment Guide

This guide provides comprehensive instructions for deploying HyFuzz in various environments, from local development to production cloud infrastructure.

## Table of Contents

- [Deployment Overview](#deployment-overview)
- [Prerequisites](#prerequisites)
- [Local Development Deployment](#local-development-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration Management](#configuration-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Strategies](#scaling-strategies)
- [Security Hardening](#security-hardening)
- [Backup and Recovery](#backup-and-recovery)
- [Maintenance](#maintenance)

## Deployment Overview

HyFuzz consists of multiple components that can be deployed together or separately:

- **Windows Server**: Control plane with LLM integration and defense systems
- **Ubuntu Client**: Payload execution engine with instrumentation
- **Ollama**: Local LLM service (optional, can use OpenAI instead)
- **Database**: SQLite (development) or PostgreSQL (production)
- **Task Queue**: Redis with Celery workers (optional, for distributed execution)
- **Dashboard**: Web-based monitoring interface

### Deployment Architectures

```
┌─────────────────────────────────────────────────────────────┐
│                    Minimal Setup (Single Machine)            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Server  │──│  Client  │──│  Ollama  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       │                                                      │
│  ┌──────────┐                                               │
│  │  SQLite  │                                               │
│  └──────────┘                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Production Setup (Distributed)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Server  │──│  Redis   │──│ Workers  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       │             │                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │PostgreSQL│  │  Nginx   │  │Dashboard │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                     │                                        │
│                ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│                │ Client 1 │  │ Client 2 │  │ Client N │   │
│                └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Hardware Requirements

**Minimum (Development)**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- Network: 100 Mbps

**Recommended (Production)**:
- Server: 8+ cores, 16+ GB RAM, 100+ GB SSD
- Client: 4+ cores, 8+ GB RAM, 50+ GB SSD
- Network: 1 Gbps, low latency between components

### Software Requirements

- **Operating System**:
  - Server: Windows Server 2019+, Ubuntu 22.04+, or compatible Linux
  - Client: Ubuntu 22.04+ (required for instrumentation tools)

- **Python**: 3.10 or higher (3.11 recommended)
- **Docker**: 24.0+ (if using containerized deployment)
- **Git**: 2.30+ (for source deployment)

### External Services

- **LLM Service** (choose one):
  - Ollama (local, free)
  - OpenAI API (cloud, requires API key)
  - Azure OpenAI (cloud, requires subscription)

- **Database** (choose one):
  - SQLite (built-in, suitable for development)
  - PostgreSQL 14+ (recommended for production)

## Local Development Deployment

Best for: Development, testing, and single-user scenarios.

### 1. Quick Start (Native Python)

```bash
# Clone repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Install dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt
pip install -r requirements-dev.txt

cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt

# Configure environment
cd ../HyFuzz-Windows-Server
cp .env.example .env
# Edit .env with your settings

cd ../HyFuzz-Ubuntu-Client
cp .env.example .env
# Edit .env with your settings

# Initialize database
cd ..
python scripts/init_database.py --demo-data

# Install and start Ollama (if using local LLM)
# See: https://ollama.ai/download
ollama serve &
ollama pull mistral

# Start server
cd HyFuzz-Windows-Server
python scripts/start_server.py

# In another terminal, start client
cd HyFuzz-Ubuntu-Client
python scripts/start_client.py

# In another terminal, start dashboard
cd HyFuzz-Windows-Server
python scripts/start_dashboard.py
```

Access dashboard at: http://localhost:8888

### 2. Using Makefile

```bash
# One-command setup
make quickstart

# Start services
make run-server &
make run-client &
make run-dashboard &

# Run a campaign
make run-campaign PROTOCOL=coap TARGET=coap://localhost:5683
```

### 3. Using Virtual Environment

```bash
# Create isolated environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r HyFuzz-Windows-Server/requirements.txt
pip install -r HyFuzz-Ubuntu-Client/requirements.txt

# Run as above
python scripts/init_database.py
python HyFuzz-Windows-Server/scripts/start_server.py
```

## Docker Deployment

Best for: Consistent environments, easy scaling, and production deployments.

### 1. Single Machine Docker Deployment

```bash
# Clone repository
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz

# Create environment files
cp HyFuzz-Windows-Server/.env.example HyFuzz-Windows-Server/.env
cp HyFuzz-Ubuntu-Client/.env.example HyFuzz-Ubuntu-Client/.env

# Edit .env files as needed
nano HyFuzz-Windows-Server/.env
nano HyFuzz-Ubuntu-Client/.env

# Start core services
docker-compose up -d server client ollama

# View logs
docker-compose logs -f server

# Start with dashboard
docker-compose --profile monitoring up -d

# Start with Redis queue
docker-compose --profile queue up -d

# Start with PostgreSQL
docker-compose --profile database up -d
```

**Verify deployment**:
```bash
# Check service health
docker-compose ps

# Test server
curl http://localhost:8080/health

# Test dashboard
curl http://localhost:8888/health

# View logs
docker-compose logs -f server client
```

### 2. Multi-Host Docker Deployment

For distributed deployment across multiple machines:

**On Control Node (Server)**:
```bash
# docker-compose.server.yml
version: '3.8'
services:
  server:
    image: hyfuzz-server:latest
    ports:
      - "8080:8080"
    environment:
      - CLIENT_ENDPOINTS=http://client1:8001,http://client2:8001
    networks:
      - hyfuzz-swarm

networks:
  hyfuzz-swarm:
    driver: overlay
```

```bash
# Initialize swarm
docker swarm init

# Deploy server
docker stack deploy -c docker-compose.server.yml hyfuzz-server
```

**On Worker Nodes (Clients)**:
```bash
# Join swarm (use token from init command)
docker swarm join --token <token> <control-node-ip>:2377

# Deploy client
docker service create \
  --name hyfuzz-client \
  --network hyfuzz-swarm \
  --env SERVER_URL=http://server:8080 \
  hyfuzz-client:latest
```

### 3. Docker Build from Source

```bash
# Build server image
cd HyFuzz-Windows-Server
docker build -t hyfuzz-server:latest .

# Build client image
cd ../HyFuzz-Ubuntu-Client
docker build -t hyfuzz-client:latest .

# Run with custom images
docker-compose up -d
```

## Production Deployment

Best for: Long-term operation, high availability, and large-scale fuzzing.

### 1. Pre-Production Checklist

- [ ] All tests pass: `make test`
- [ ] Health check succeeds: `python scripts/health_check.py --verbose`
- [ ] Configuration reviewed and secured
- [ ] Secrets managed securely (not in .env files)
- [ ] Database backup configured
- [ ] Monitoring and alerting configured
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates obtained
- [ ] Resource limits configured
- [ ] Log rotation configured

### 2. Production Configuration

**Environment Variables** (use secrets management):
```bash
# DO NOT use .env files in production
# Use environment variables or secrets management

# Server
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8080
export DATABASE_URL=postgresql://user:pass@db-server:5432/hyfuzz
export OLLAMA_ENDPOINT=http://ollama-server:11434
export LOG_LEVEL=INFO
export ENVIRONMENT=production

# Security
export SECRET_KEY=$(openssl rand -hex 32)
export API_KEY=$(openssl rand -hex 32)
export ALLOWED_HOSTS=server.example.com

# Client
export SERVER_URL=https://server.example.com
export CLIENT_ID=client-prod-01
export INSTRUMENTATION_ENABLED=true
```

**Database Configuration** (PostgreSQL):
```bash
# Initialize production database
python scripts/init_database.py \
  --database-url postgresql://hyfuzz:password@db-server:5432/hyfuzz

# Or use migrations (if using Alembic)
alembic upgrade head
```

**Reverse Proxy** (Nginx):
```nginx
# /etc/nginx/sites-available/hyfuzz
server {
    listen 80;
    server_name hyfuzz.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hyfuzz.example.com;

    ssl_certificate /etc/letsencrypt/live/hyfuzz.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hyfuzz.example.com/privkey.pem;

    # Server
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard
    location /dashboard {
        proxy_pass http://localhost:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Systemd Services**:

Create `/etc/systemd/system/hyfuzz-server.service`:
```ini
[Unit]
Description=HyFuzz Server
After=network.target postgresql.service

[Service]
Type=simple
User=hyfuzz
Group=hyfuzz
WorkingDirectory=/opt/hyfuzz
Environment="PYTHONPATH=/opt/hyfuzz"
EnvironmentFile=/opt/hyfuzz/.env.production
ExecStart=/opt/hyfuzz/venv/bin/python scripts/start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/hyfuzz-workers.service`:
```ini
[Unit]
Description=HyFuzz Workers
After=network.target hyfuzz-server.service

[Service]
Type=simple
User=hyfuzz
Group=hyfuzz
WorkingDirectory=/opt/hyfuzz
EnvironmentFile=/opt/hyfuzz/.env.production
ExecStart=/opt/hyfuzz/venv/bin/python scripts/start_workers.py --concurrency 8
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hyfuzz-server hyfuzz-workers
sudo systemctl start hyfuzz-server hyfuzz-workers
sudo systemctl status hyfuzz-server hyfuzz-workers
```

### 3. Resource Limits

**Systemd Resource Limits** (add to service files):
```ini
[Service]
# Memory
MemoryMax=8G
MemoryHigh=7G

# CPU
CPUQuota=400%  # 4 cores max

# File limits
LimitNOFILE=65536
```

**Docker Resource Limits** (docker-compose.yml):
```yaml
services:
  server:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

## Cloud Deployment

### AWS Deployment

**Architecture**:
- EC2 instances for server and clients
- RDS PostgreSQL for database
- ElastiCache Redis for task queue
- ELB for load balancing
- S3 for artifact storage
- CloudWatch for monitoring

**Deployment Steps**:

1. **Launch EC2 Instances**:
```bash
# Server instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.large \
  --key-name hyfuzz-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=hyfuzz-server}]'

# Client instances (repeat for multiple clients)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name hyfuzz-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=hyfuzz-client-1}]'
```

2. **Create RDS Database**:
```bash
aws rds create-db-instance \
  --db-instance-identifier hyfuzz-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username hyfuzz \
  --master-user-password <secure-password> \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxxxx
```

3. **Deploy Application**:
```bash
# SSH to server instance
ssh -i hyfuzz-key.pem ubuntu@<server-ip>

# Clone and setup
git clone https://github.com/your-org/HyFuzz.git
cd HyFuzz
make install

# Configure with RDS endpoint
export DATABASE_URL=postgresql://hyfuzz:password@hyfuzz-db.xxxxx.rds.amazonaws.com:5432/hyfuzz

# Start services
sudo systemctl start hyfuzz-server
```

**Terraform Configuration** (infrastructure as code):
```hcl
# main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "hyfuzz_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.large"

  tags = {
    Name = "hyfuzz-server"
  }

  user_data = file("setup-server.sh")
}

resource "aws_db_instance" "hyfuzz_db" {
  identifier        = "hyfuzz-db"
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  username          = "hyfuzz"
  password          = var.db_password
}

# Output endpoints
output "server_ip" {
  value = aws_instance.hyfuzz_server.public_ip
}
```

### Azure Deployment

**Architecture**:
- Azure VMs for server and clients
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Load Balancer
- Azure Blob Storage for artifacts
- Azure Monitor for monitoring

**Deployment Steps**:

1. **Create Resource Group**:
```bash
az group create --name hyfuzz-rg --location eastus
```

2. **Create Database**:
```bash
az postgres server create \
  --resource-group hyfuzz-rg \
  --name hyfuzz-db \
  --location eastus \
  --admin-user hyfuzz \
  --admin-password <secure-password> \
  --sku-name B_Gen5_2
```

3. **Create VMs and Deploy**:
```bash
# Server VM
az vm create \
  --resource-group hyfuzz-rg \
  --name hyfuzz-server \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub

# Deploy application
ssh azureuser@<server-ip>
# Follow standard deployment steps
```

### Google Cloud Platform (GCP) Deployment

**Architecture**:
- Compute Engine instances
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Load Balancing
- Cloud Storage for artifacts
- Cloud Monitoring

**Deployment Steps**:

1. **Create Instances**:
```bash
# Server instance
gcloud compute instances create hyfuzz-server \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# Client instances
gcloud compute instances create hyfuzz-client-1 \
  --zone=us-central1-a \
  --machine-type=n1-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud
```

2. **Create Cloud SQL**:
```bash
gcloud sql instances create hyfuzz-db \
  --database-version=POSTGRES_14 \
  --tier=db-n1-standard-2 \
  --region=us-central1
```

### Kubernetes Deployment

Best for: Large-scale, highly available deployments with auto-scaling.

**Kubernetes Manifests** (k8s/):

`server-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hyfuzz-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hyfuzz-server
  template:
    metadata:
      labels:
        app: hyfuzz-server
    spec:
      containers:
      - name: server
        image: hyfuzz-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hyfuzz-secrets
              key: database-url
        - name: OLLAMA_ENDPOINT
          value: "http://ollama-service:11434"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: hyfuzz-server
spec:
  selector:
    app: hyfuzz-server
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: LoadBalancer
```

`client-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hyfuzz-client
spec:
  replicas: 5
  selector:
    matchLabels:
      app: hyfuzz-client
  template:
    metadata:
      labels:
        app: hyfuzz-client
    spec:
      containers:
      - name: client
        image: hyfuzz-client:latest
        env:
        - name: SERVER_URL
          value: "http://hyfuzz-server:8080"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        securityContext:
          capabilities:
            add:
            - SYS_PTRACE
```

**Deploy to Kubernetes**:
```bash
# Create namespace
kubectl create namespace hyfuzz

# Create secrets
kubectl create secret generic hyfuzz-secrets \
  --from-literal=database-url=postgresql://user:pass@db:5432/hyfuzz \
  --namespace=hyfuzz

# Deploy
kubectl apply -f k8s/ --namespace=hyfuzz

# Scale clients
kubectl scale deployment hyfuzz-client --replicas=10 --namespace=hyfuzz

# View status
kubectl get pods --namespace=hyfuzz
kubectl logs -f deployment/hyfuzz-server --namespace=hyfuzz
```

## Configuration Management

### Using Environment Variables

```bash
# Production environment
export HYFUZZ_ENV=production
export HYFUZZ_CONFIG_PATH=/etc/hyfuzz/config.yaml
export HYFUZZ_SECRETS_PATH=/etc/hyfuzz/secrets.yaml
```

### Using Configuration Files

**config/production.yaml**:
```yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 8

database:
  url: postgresql://user:pass@db-server:5432/hyfuzz
  pool_size: 20
  max_overflow: 10

llm:
  provider: ollama
  endpoint: http://ollama-server:11434
  model: mistral
  timeout: 120

defense:
  enabled: true
  modules:
    - behavioral
    - signature
    - anomaly

logging:
  level: INFO
  format: json
  output: /var/log/hyfuzz/server.log

monitoring:
  enabled: true
  metrics_port: 9090
```

### Secrets Management

**AWS Secrets Manager**:
```bash
# Store secret
aws secretsmanager create-secret \
  --name hyfuzz/database-url \
  --secret-string "postgresql://user:pass@db:5432/hyfuzz"

# Retrieve in application
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='hyfuzz/database-url')
database_url = secret['SecretString']
```

**HashiCorp Vault**:
```bash
# Store secret
vault kv put secret/hyfuzz/config \
  database_url="postgresql://user:pass@db:5432/hyfuzz"

# Retrieve
vault kv get -field=database_url secret/hyfuzz/config
```

## Monitoring and Logging

### Application Monitoring

**Prometheus** (metrics collection):

`prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hyfuzz-server'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'hyfuzz-client'
    static_configs:
      - targets: ['client1:9091', 'client2:9091']
```

**Grafana** (visualization):

Dashboard configuration for HyFuzz metrics:
- Campaign success rate
- Payload generation rate
- Defense system verdicts
- Resource utilization
- Error rates

### Logging Configuration

**Centralized Logging** (ELK Stack):

`filebeat.yml`:
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/hyfuzz/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "hyfuzz-%{+yyyy.MM.dd}"
```

**Log Rotation** (logrotate):

`/etc/logrotate.d/hyfuzz`:
```
/var/log/hyfuzz/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 hyfuzz hyfuzz
    sharedscripts
    postrotate
        systemctl reload hyfuzz-server
    endscript
}
```

### Alerting

**Prometheus Alertmanager** rules:

`alerts.yml`:
```yaml
groups:
- name: hyfuzz
  rules:
  - alert: HighErrorRate
    expr: rate(hyfuzz_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: ServerDown
    expr: up{job="hyfuzz-server"} == 0
    for: 1m
    annotations:
      summary: "HyFuzz server is down"
```

## Scaling Strategies

### Horizontal Scaling

**Scale Clients**:
```bash
# Docker Swarm
docker service scale hyfuzz-client=10

# Kubernetes
kubectl scale deployment hyfuzz-client --replicas=10

# Manually
for i in {1..10}; do
    python scripts/start_client.py --client-id "client-$i" &
done
```

**Scale Workers**:
```bash
# Increase worker concurrency
export WORKER_CONCURRENCY=16
python scripts/start_workers.py --concurrency 16

# Or multiple worker processes
for i in {1..4}; do
    python scripts/start_workers.py --concurrency 4 &
done
```

### Vertical Scaling

**Increase Resources**:
```bash
# Update systemd service limits
sudo systemctl edit hyfuzz-server

# Add:
[Service]
MemoryMax=16G
CPUQuota=800%
```

### Load Balancing

**Nginx Load Balancer**:
```nginx
upstream hyfuzz_servers {
    least_conn;
    server server1:8080 max_fails=3 fail_timeout=30s;
    server server2:8080 max_fails=3 fail_timeout=30s;
    server server3:8080 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    location / {
        proxy_pass http://hyfuzz_servers;
    }
}
```

## Security Hardening

### Network Security

**Firewall Rules** (ufw):
```bash
# Server
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8080/tcp  # Server API
sudo ufw allow 8888/tcp  # Dashboard
sudo ufw enable

# Client
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8001/tcp  # Client API (from server only)
sudo ufw enable
```

**AWS Security Groups**:
```bash
# Server security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0

# Client security group (only from server)
aws ec2 authorize-security-group-ingress \
  --group-id sg-yyyyy \
  --protocol tcp \
  --port 8001 \
  --source-group sg-xxxxx
```

### Application Security

**Enable Authentication**:
```python
# In .env or environment
export API_KEY=$(openssl rand -hex 32)
export JWT_SECRET=$(openssl rand -hex 32)
export REQUIRE_AUTH=true
```

**SSL/TLS**:
```bash
# Obtain Let's Encrypt certificate
sudo certbot --nginx -d hyfuzz.example.com

# Or use self-signed for development
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes
```

**Input Validation**:
Ensure all user inputs are validated (already implemented in HyFuzz using Pydantic models).

### Secrets Management

**Never commit secrets**:
```bash
# Verify no secrets in git
git secrets --scan

# Use environment variables or secrets manager
export DATABASE_PASSWORD=$(aws secretsmanager get-secret-value ...)
```

## Backup and Recovery

### Database Backup

**SQLite Backup**:
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR=/backups/hyfuzz
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 data/hyfuzz.db ".backup $BACKUP_DIR/hyfuzz_$DATE.db"

# Compress
gzip $BACKUP_DIR/hyfuzz_$DATE.db

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

**PostgreSQL Backup**:
```bash
# Automated backup
pg_dump -h db-server -U hyfuzz hyfuzz | gzip > /backups/hyfuzz_$(date +%Y%m%d).sql.gz

# Or use pg_basebackup for continuous archiving
pg_basebackup -h db-server -D /backups/base -U replication -X stream
```

**Automated Backup** (cron):
```bash
# /etc/cron.d/hyfuzz-backup
0 2 * * * hyfuzz /opt/hyfuzz/scripts/backup.sh
```

### Disaster Recovery

**Recovery Procedure**:

1. **Restore Database**:
```bash
# SQLite
cp /backups/hyfuzz_20240101.db data/hyfuzz.db

# PostgreSQL
gunzip < /backups/hyfuzz_20240101.sql.gz | psql -h db-server -U hyfuzz hyfuzz
```

2. **Restore Configuration**:
```bash
cp /backups/config/.env.production .env
cp /backups/config/*.yaml config/
```

3. **Restart Services**:
```bash
sudo systemctl restart hyfuzz-server hyfuzz-workers
```

4. **Verify**:
```bash
python scripts/health_check.py --verbose
```

## Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor logs for errors
- Check service health
- Review campaign metrics

**Weekly**:
- Review resource utilization
- Check for security updates
- Analyze performance metrics
- Clean up old logs

**Monthly**:
- Update dependencies
- Review and archive old campaigns
- Database maintenance (vacuum, analyze)
- Capacity planning review

### Update Procedure

```bash
# 1. Backup current state
./scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations (if any)
python scripts/migrate_database.py

# 5. Restart services
sudo systemctl restart hyfuzz-server hyfuzz-workers

# 6. Verify
python scripts/health_check.py --verbose
```

### Database Maintenance

```bash
# SQLite
sqlite3 data/hyfuzz.db "VACUUM;"
sqlite3 data/hyfuzz.db "ANALYZE;"

# PostgreSQL
psql -h db-server -U hyfuzz hyfuzz -c "VACUUM ANALYZE;"
```

### Log Cleanup

```bash
# Clean logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete

# Compress old logs
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

---

## Quick Reference

### Deployment Commands

```bash
# Local Development
make quickstart

# Docker (Single Machine)
docker-compose up -d

# Docker (Production with all services)
docker-compose --profile monitoring --profile queue --profile database up -d

# Kubernetes
kubectl apply -f k8s/ --namespace=hyfuzz

# Systemd
sudo systemctl start hyfuzz-server hyfuzz-workers
```

### Health Checks

```bash
# Application health
curl http://localhost:8080/health

# Database
python scripts/init_database.py --verify

# Full system
python scripts/health_check.py --verbose
```

### Monitoring

```bash
# View logs
docker-compose logs -f server
journalctl -u hyfuzz-server -f

# Check resources
docker stats
htop

# View metrics
curl http://localhost:9090/metrics
```

---

For additional help:
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)

**Production Support**: For enterprise deployment assistance, contact support@hyfuzz.example.com
