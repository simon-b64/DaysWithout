# Days Without - Docker Deployment

## Quick Start

### Option 1: Use Pre-built Image from GitHub Container Registry

Pull and run the latest image:
```bash
docker pull ghcr.io/OWNER/dayswithout:latest
docker run -p 5000:5000 -v days-without-data:/app/instance ghcr.io/OWNER/dayswithout:latest
```

Or update docker-compose.yml to use the pre-built image:
```yaml
services:
  web:
    image: ghcr.io/OWNER/dayswithout:latest
    # ... rest of config
```

Replace `OWNER` with your GitHub username or organization name.

### Option 2: Build and run with Docker Compose:
```bash
docker-compose up -d
```

### Stop the application:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f
```

## Configuration

### Option 1: Using Environment Variables (Recommended for Docker)
The app uses default settings from `app/__init__.py`. For production, you should change the SECRET_KEY.

### Option 2: Using a Config File
1. Copy the example config:
   ```bash
   copy config.py.example instance\config.py
   ```

2. Edit `instance/config.py` and set a strong SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex())"
   ```

3. Uncomment the config volume mount in `docker-compose.yml`:
   ```yaml
   - ./instance/config.py:/app/instance/config.py:ro
   ```

4. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Data Persistence

The SQLite database is stored in a Docker volume called `days-without-data`. This means your data persists even if you remove and recreate containers.

To backup your database:
```bash
docker-compose exec web cat /app/instance/days_without.sqlite > backup.sqlite
```

To restore from backup:
```bash
docker-compose exec -T web sh -c "cat > /app/instance/days_without.sqlite" < backup.sqlite
docker-compose restart
```

## Accessing the Application
## Automated Builds (CI/CD)

This project includes a GitHub Actions workflow that automatically:
- Builds the Docker image on every push to the master branch
- Pushes the image to GitHub Container Registry (GHCR)
- Tags the image with:
  - `latest` (for master branch)
  - `master` (branch name)
  - `master-<git-sha>` (specific commit)

### Making Images Public

By default, GHCR images are private. To make your image public:
1. Go to your GitHub repository
2. Navigate to Packages → Your package
3. Click "Package settings"
4. Scroll down to "Danger Zone"
5. Click "Change visibility" → "Public"

### Using the Automated Builds

After pushing to master, the image will be available at:
```
ghcr.io/<your-github-username>/dayswithout:latest
```

Pull and use it:
```bash
docker pull ghcr.io/<your-github-username>/dayswithout:latest
docker run -p 5000:5000 ghcr.io/<your-github-username>/dayswithout:latest
```



Once running, access the application at:
- http://localhost:5000

To use a different port, edit the `ports` section in `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Access at localhost:8080
```

## Production Deployment

For production:
1. Set a strong SECRET_KEY (either in config.py or environment variable)
2. Consider using a reverse proxy (nginx, traefik) for HTTPS
3. Regular database backups
4. Monitor logs: `docker-compose logs -f`

