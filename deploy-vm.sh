#!/bin/bash
# Deployment script for SocialMediaPostGenerator VM
# This script creates the GCP VM instance

set -e  # Exit on error

# Configuration
PROJECT_ID="tonal-carving-485119-q7"
VM_NAME="socialmedia-post-generator"
ZONE="us-east1-b"
MACHINE_TYPE="e2-small"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
BOOT_DISK_SIZE="10GB"
STARTUP_SCRIPT="startup-script.sh"

echo "=== Deploying SocialMediaPostGenerator VM ==="
echo "Project: $PROJECT_ID"
echo "VM Name: $VM_NAME"
echo "Zone: $ZONE"
echo "Machine Type: $MACHINE_TYPE"
echo ""

# Set the project
echo "Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Check if startup script exists
if [ ! -f "$STARTUP_SCRIPT" ]; then
    echo "Error: Startup script '$STARTUP_SCRIPT' not found!"
    exit 1
fi

# Create the VM instance
echo "Creating VM instance..."
gcloud compute instances create "$VM_NAME" \
    --zone="$ZONE" \
    --machine-type="$MACHINE_TYPE" \
    --image-family="$IMAGE_FAMILY" \
    --image-project="$IMAGE_PROJECT" \
    --boot-disk-size="$BOOT_DISK_SIZE" \
    --boot-disk-type=pd-standard \
    --metadata-from-file startup-script="$STARTUP_SCRIPT" \
    --tags=http-server,https-server \
    --scopes=https://www.googleapis.com/auth/cloud-platform

echo ""
echo "=== VM created successfully! ==="
echo "Instance: $VM_NAME"
echo "Zone: $ZONE"
echo ""
echo "Waiting for VM to be ready (this may take a minute)..."
sleep 30

# Get the external IP
EXTERNAL_IP=$(gcloud compute instances describe "$VM_NAME" \
    --zone="$ZONE" \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo "VM External IP: $EXTERNAL_IP"
echo ""
echo "Next steps:"
echo "1. Wait a few minutes for the startup script to complete"
echo "2. Run: ./setup-app.sh to transfer application files"
echo "3. SSH into VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
