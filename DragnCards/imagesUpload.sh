#!/bin/bash
# Install AWS CLI
# Create ~/.aws/credentials
# pip3 install boto3
# * * * * * flock -xn /var/www/dragncards.com/dragncards/frontend/images_upload.lock -c '/var/www/dragncards.com/dragncards/frontend/imagesUpload.sh'
cd "$(dirname "$0")"
python3 images_upload.py "$1"
