# InventoryX production deployment (Docker Compose + Caddy)

This deployment profile is intended for a Linux VPS with a DNS name that points to the server. It is a deployment template, not a live deployment.

## Prerequisites

- A Linux VPS with Docker Engine and the Docker Compose plugin.
- A domain or subdomain with an A/AAAA record pointing to the VPS.
- Inbound TCP ports 80 and 443 available for Caddy's automatic HTTPS certificate.

## Configure secrets

From the repository root:

```bash
cp .env.production.example .env.production
openssl rand -hex 32
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated hex value in POSTGRES_PASSWORD and the token-safe value in SECRET_KEY. Set DOMAIN to the DNS name pointing to the VPS. Keep .env.production private and never commit it.

The database password uses hexadecimal characters so it can safely be interpolated into the PostgreSQL URL in the Compose file.

## Start the stack

From the repository root:

```bash
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml up --build -d
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml ps
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml logs -f api
```

The API container applies Alembic migrations before Uvicorn starts. PostgreSQL is not published to the public host. Caddy obtains and renews HTTPS certificates and proxies requests to the API.

Verify:

- https://YOUR_DOMAIN/health
- https://YOUR_DOMAIN/docs

## Operations

```bash
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml exec db pg_dump -U inventoryx inventoryx > inventoryx-backup.sql
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml pull caddy
docker compose --env-file .env.production -f deploy/docker-compose.prod.yml up -d
```

Store database backups off the VPS and test restores. Configure VPS firewall rules, OS updates, monitoring, log retention, and an external backup policy. Do not expose the PostgreSQL port. Review whether public Swagger docs should be disabled or protected for the deployed environment.

## Deployment status

No cloud account, DNS zone, VPS, or production secrets are connected through this repository workflow. The template must be configured and deployed in your hosting account before a public demo URL can be supplied.
