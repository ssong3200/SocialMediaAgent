#!/bin/bash
# Setup script for SocialMediaPostGenerator application
# This script transfers application files and configures the environment

set -e  # Exit on error

# Configuration
VM_NAME="socialmedia-post-generator"
ZONE="us-east1-b"
APP_DIR="/opt/socialmedia-agent"
REMOTE_USER=$(gcloud config get-value account 2>/dev/null | cut -d'@' -f1 || echo "$USER")

echo "=== Setting up SocialMediaPostGenerator application ==="
echo "VM: $VM_NAME"
echo "Zone: $ZONE"
echo "Remote directory: $APP_DIR"
echo ""

# Check if .env file exists locally
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found in current directory."
    echo "You'll need to create it on the VM manually or use GCP Secret Manager."
    echo ""
fi

# Create remote directory structure
echo "Creating remote directory structure..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="sudo mkdir -p $APP_DIR && sudo chown -R $USER:$USER $APP_DIR" 2>/dev/null || \
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="mkdir -p $APP_DIR"

# Transfer application files
echo "Transferring application files..."
FILES_TO_TRANSFER=(
    "generate.py"
    "post_generator.py"
    "brand_context.py"
    "requirements.txt"
    "README.md"
)

for file in "${FILES_TO_TRANSFER[@]}"; do
    if [ -f "$file" ]; then
        echo "  Transferring $file..."
        gcloud compute scp "$file" "$VM_NAME:$APP_DIR/" --zone="$ZONE"
    else
        echo "  Warning: $file not found, skipping..."
    fi
done

# Transfer .env file if it exists (with warning about security)
if [ -f ".env" ]; then
    echo ""
    echo "Transferring .env file (contains sensitive API keys)..."
    gcloud compute scp ".env" "$VM_NAME:$APP_DIR/.env" --zone="$ZONE"
    echo "  Note: Consider using GCP Secret Manager for production deployments"
else
    echo ""
    echo "No .env file found. You'll need to create it manually on the VM."
fi

# Install Python dependencies on the VM
echo ""
echo "Installing Python dependencies on VM..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    cd $APP_DIR && \
    if [ ! -d venv ]; then \
        python3 -m venv venv; \
    fi && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt
"

# Create a simple test script
echo ""
echo "Creating test script..."
cat > /tmp/test-app.sh << 'TESTEOF'
#!/bin/bash
cd /opt/socialmedia-agent
source venv/bin/activate
python3 generate.py --platform mastodon --help
TESTEOF

gcloud compute scp /tmp/test-app.sh "$VM_NAME:$APP_DIR/test-app.sh" --zone="$ZONE"
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="chmod +x $APP_DIR/test-app.sh"
rm /tmp/test-app.sh

echo ""
echo "=== Application setup complete! ==="
echo ""
echo "To test the application, SSH into the VM:"
echo "  gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "Then run:"
echo "  cd $APP_DIR"
echo "  source venv/bin/activate"
echo "  python3 generate.py --platform mastodon"
echo ""
echo "Or use the test script:"
echo "  $APP_DIR/test-app.sh"
