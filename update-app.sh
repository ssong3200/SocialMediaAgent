#!/bin/bash
# Quick update script for deploying code changes
# This script transfers updated files and restarts the service

set -e  # Exit on error

VM_NAME="socialmedia-post-generator"
ZONE="us-east1-b"
APP_DIR="/opt/socialmedia-agent"

echo "=== Updating Social Media Agent Application ==="
echo "VM: $VM_NAME"
echo "Zone: $ZONE"
echo ""

# Files to update (add more as needed)
FILES_TO_UPDATE=(
    "app.py"
    "post_generator.py"
    "generate.py"
    "brand_context.py"
    "requirements.txt"
)

# Transfer updated files
echo "Transferring updated files..."
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        echo "  → $file"
        gcloud compute scp "$file" "$VM_NAME:$APP_DIR/" --zone="$ZONE"
    else
        echo "  ⚠️  $file not found, skipping..."
    fi
done

# Update Python dependencies if requirements.txt changed
if [[ " ${FILES_TO_UPDATE[@]} " =~ " requirements.txt " ]]; then
    echo ""
    echo "Updating Python dependencies..."
    gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
        cd $APP_DIR && \
        source venv/bin/activate && \
        pip install --upgrade pip -q && \
        pip install -r requirements.txt -q && \
        echo 'Dependencies updated'
    "
fi

# Restart the service
echo ""
echo "Restarting FastAPI service..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    sudo systemctl restart socialmedia-api && \
    sleep 2 && \
    sudo systemctl status socialmedia-api --no-pager | head -5
"

echo ""
echo "=== Update Complete! ==="
echo ""
echo "Service restarted. Changes should be live now."
echo ""
echo "To check service status:"
echo "  gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo systemctl status socialmedia-api'"
echo ""
echo "To view logs:"
echo "  gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo journalctl -u socialmedia-api -n 50'"
