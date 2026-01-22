# Deployment Guide

## Initial Deployment

For the first-time setup, use:
```bash
./deploy-vm.sh        # Creates the VM (only needed once)
./setup-app.sh        # Transfers files and sets up environment
./deploy-fastapi.sh   # Deploys FastAPI and SQLite
```

## Updating Code

After making code changes, use the quick update script:
```bash
./update-app.sh
```

This script will:
- Transfer updated files to the VM
- Update Python dependencies if `requirements.txt` changed
- Restart the FastAPI service
- Show service status

## What Gets Updated

The `update-app.sh` script updates these files by default:
- `app.py` - FastAPI application
- `post_generator.py` - Post generator logic
- `generate.py` - CLI tool
- `brand_context.py` - Brand context
- `requirements.txt` - Python dependencies

## Manual Update Process

If you need more control, you can manually update:

1. **Transfer a specific file:**
   ```bash
   gcloud compute scp app.py socialmedia-post-generator:/opt/socialmedia-agent/ --zone=us-east1-b
   ```

2. **Restart the service:**
   ```bash
   gcloud compute ssh socialmedia-post-generator --zone=us-east1-b \
     --command="sudo systemctl restart socialmedia-api"
   ```

3. **Update dependencies:**
   ```bash
   gcloud compute ssh socialmedia-post-generator --zone=us-east1-b --command="
     cd /opt/socialmedia-agent && \
     source venv/bin/activate && \
     pip install -r requirements.txt
   "
   ```

## Service Management

**Check service status:**
```bash
gcloud compute ssh socialmedia-post-generator --zone=us-east1-b \
  --command="sudo systemctl status socialmedia-api"
```

**View logs:**
```bash
gcloud compute ssh socialmedia-post-generator --zone=us-east1-b \
  --command="sudo journalctl -u socialmedia-api -f"
```

**Restart service:**
```bash
gcloud compute ssh socialmedia-post-generator --zone=us-east1-b \
  --command="sudo systemctl restart socialmedia-api"
```

## Database Location

The SQLite database is stored at:
```
/opt/socialmedia-agent/posts.db
```

To backup the database:
```bash
gcloud compute scp socialmedia-post-generator:/opt/socialmedia-agent/posts.db ./posts-backup.db --zone=us-east1-b
```

## Adding New Files

If you add new Python files, update the `FILES_TO_UPDATE` array in `update-app.sh`:
```bash
FILES_TO_UPDATE=(
    "app.py"
    "post_generator.py"
    "your_new_file.py"  # Add here
)
```

## Hot Reload (Development)

For development, you can run FastAPI with auto-reload (not recommended for production):
```bash
gcloud compute ssh socialmedia-post-generator --zone=us-east1-b --command="
  cd /opt/socialmedia-agent && \
  source venv/bin/activate && \
  uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"
```

Note: This won't persist after SSH session ends. Use systemd service for production.
