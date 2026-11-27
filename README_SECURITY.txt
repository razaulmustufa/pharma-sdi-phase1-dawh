# GitHub-safe Docker Compose configuration

This folder contains a sanitized `docker-compose.yaml` suitable for a public repository.

## Local use

1. Copy `.env.example` to `.env` in the same directory as `docker-compose.yaml`.
2. Replace every placeholder with real local values. Generate a valid Fernet key and a long random JWT secret.
3. Use a strong PostgreSQL password. Because it appears inside a PostgreSQL URL, use URL-safe characters or URL-encode special characters.
4. Keep `.env` private and do not upload it to GitHub.
5. Do not replace your currently working local compose file with this template unless you have configured `.env` and are ready to test the updated credentials.

The original uploaded file is not modified. This sanitized copy is intended for repository documentation/reproducibility and requires the local `.env` values before it can run.
