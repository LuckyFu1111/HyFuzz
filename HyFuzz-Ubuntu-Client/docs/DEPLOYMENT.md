# Deployment Guide

Deploy the HyFuzz Ubuntu client on bare metal, virtual machines, or containers depending on your
infrastructure. This guide outlines the recommended approaches.

## Bare Metal or VM Deployment

1. Follow the [Setup Guide](SETUP.md) to install dependencies and configure the environment.
2. Create a systemd service for long-running campaigns:
   ```ini
   [Unit]
   Description=HyFuzz Client
   After=network-online.target

   [Service]
   WorkingDirectory=/opt/hyfuzz-client
   EnvironmentFile=/opt/hyfuzz-client/.env
   ExecStart=/opt/hyfuzz-client/venv/bin/python scripts/start_client.py --config config/example_configs/config_prod.yaml
   Restart=on-failure
   LimitCORE=infinity

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo cp hyfuzz-client.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now hyfuzz-client.service
   ```
3. Rotate logs using the maintenance scripts or logrotate.
4. Use `systemctl status hyfuzz-client` to monitor service health.

## Container Deployment (Docker/Podman)

1. Build the image:
   ```bash
   docker build -f docker/client.dockerfile -t hyfuzz-client:latest .
   ```
2. Run the container:
   ```bash
   docker run --rm -d \
     --name hyfuzz-client \
     --net host \
     -v /opt/hyfuzz/data:/app/data \
     -v /opt/hyfuzz/logs:/app/logs \
     --env-file /opt/hyfuzz/.env \
     hyfuzz-client:latest
   ```
3. Use `docker logs -f hyfuzz-client` to stream execution logs.
4. For multiple clients, leverage docker-compose or Kubernetes to scale horizontally.

## Distributed Pools

- Run the deployment steps on each worker node.
- Configure distinct client IDs in `.env` (`CLIENT_ID`) for easier tracking.
- Use `scripts/start_workers.py` and `scripts/stop_workers.py` to manage worker pools programmatically.
- Monitor aggregated metrics through the server dashboard or Prometheus exporters.

## Updating Clients

1. Pull the latest code:
   ```bash
   git pull origin main
   ```
2. Apply migrations or schema updates (if any) using `scripts/database/migrate.py`.
3. Reinstall dependencies when `requirements*.txt` changes:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Restart services or containers to pick up changes.

## Backup & Restore

- Back up the SQLite database and reports regularly:
  ```bash
  python scripts/backup_results.py --destination /mnt/backups/hyfuzz
  ```
- Restore from backup when needed:
  ```bash
  python scripts/restore_results.py --source /mnt/backups/hyfuzz
  ```
- Store backups securely and test restore procedures quarterly.

## Security Hardening

- Run the client under a dedicated user account with limited privileges.
- Restrict outbound network access to approved destinations (HyFuzz server, telemetry endpoints).
- Keep the host patched and enable automatic security updates.
- Monitor system logs (`/var/log/syslog`, `/var/log/auth.log`) for anomalies.

## Validation Checklist

- [ ] `.env` configured with correct server endpoint and credentials.
- [ ] Required ports open between client and server.
- [ ] Sandboxing prerequisites satisfied (namespaces, cgroups, ptrace permissions).
- [ ] Monitoring and alerting verified (`scripts/monitor_client.py --once`).
- [ ] Backups scheduled and tested.

For operational procedures after deployment, review [`USAGE.md`](USAGE.md) and [`MONITORING.md`](MONITORING.md).
