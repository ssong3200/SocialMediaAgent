#!/bin/bash
# Deployment script for FastAPI application
# This script deploys the FastAPI app and sets up the systemd service

set -e  # Exit on error

VM_NAME="socialmedia-post-generator"
ZONE="us-east1-b"
APP_DIR="/opt/socialmedia-agent"

echo "=== Deploying FastAPI Application ==="
echo "VM: $VM_NAME"
echo "Zone: $ZONE"
echo ""

# Transfer app.py
echo "Transferring FastAPI application..."
gcloud compute scp app.py "$VM_NAME:$APP_DIR/" --zone="$ZONE"

# Transfer updated requirements.txt
echo "Transferring updated requirements..."
gcloud compute scp requirements.txt "$VM_NAME:$APP_DIR/" --zone="$ZONE"

# Install FastAPI dependencies
echo "Installing FastAPI dependencies..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    cd $APP_DIR && \
    source venv/bin/activate && \
    pip install --upgrade pip -q && \
    pip install -r requirements.txt -q && \
    echo 'FastAPI dependencies installed'
"

# Transfer systemd service file
echo "Setting up systemd service..."
gcloud compute scp socialmedia-api.service "$VM_NAME:/tmp/" --zone="$ZONE"

# Install and enable service
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    sudo mv /tmp/socialmedia-api.service /etc/systemd/system/ && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable socialmedia-api.service && \
    sudo systemctl start socialmedia-api.service && \
    echo 'Service installed and started'
"

# Configure firewall rule
echo "Configuring firewall rule..."
gcloud compute firewall-rules create allow-fastapi \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow FastAPI on port 8000" \
    --project tonal-carving-485119-q7 2>/dev/null || \
    echo "Firewall rule may already exist"

# Get VM external IP
EXTERNAL_IP=$(gcloud compute instances describe "$VM_NAME" \
    --zone="$ZONE" \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "FastAPI is running on: http://$EXTERNAL_IP:8000"
echo ""
echo "API Endpoints:"
echo "  - Health: http://$EXTERNAL_IP:8000/health"
echo "  - Docs: http://$EXTERNAL_IP:8000/docs"
echo "  - Generate Post: POST http://$EXTERNAL_IP:8000/api/posts/generate"
echo "  - List Posts: GET http://$EXTERNAL_IP:8000/api/posts"
echo ""
echo "To check service status:"
echo "  gcloud compute ssh $VM_NAME --zone=$ZONE --command='sudo systemctl status socialmedia-api'"
