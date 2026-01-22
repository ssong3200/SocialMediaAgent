#!/bin/bash
# Startup script for SocialMediaPostGenerator VM
# This script runs when the VM boots up

set -e  # Exit on error

echo "=== Starting SocialMediaPostGenerator VM setup ==="

# Update system packages
echo "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install Python 3.10+ and pip
echo "Installing Python 3.10+ and pip..."
apt-get install -y python3 python3-pip python3-venv

# Install required system dependencies
echo "Installing system dependencies..."
apt-get install -y \
    build-essential \
    curl \
    git \
    wget

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/socialmedia-agent
cd /opt/socialmedia-agent

# Create a virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies (will be done after files are transferred)
echo "Python environment ready. Application files will be installed separately."

# Create a non-root user for running the application (optional, for security)
echo "Setup complete. Application files should be transferred separately."

# Log completion
echo "=== VM setup completed at $(date) ===" >> /var/log/vm-setup.log
