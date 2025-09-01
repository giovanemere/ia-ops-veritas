#!/bin/bash

echo "🗂️  Setting up MinIO for IA-Ops Veritas Reports..."

MINIO_HOST="localhost:9898"
BUCKET_NAME="veritas-reports"

# Check if MinIO is running
if ! curl -s http://$MINIO_HOST/minio/health/live > /dev/null; then
    echo "❌ MinIO not running. Please start MinIO first."
    exit 1
fi

# Install mc if needed
if ! command -v mc &> /dev/null; then
    echo "📦 Installing MinIO client..."
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
fi

# Configure MinIO
echo "🔗 Configuring MinIO..."
mc alias set veritas http://$MINIO_HOST minioadmin minioadmin

# Create bucket and folders
echo "📁 Creating bucket structure..."
mc mb veritas/$BUCKET_NAME --ignore-existing
mc mkdir veritas/$BUCKET_NAME/projects --ignore-existing
mc mkdir veritas/$BUCKET_NAME/executions --ignore-existing
mc mkdir veritas/$BUCKET_NAME/evidence --ignore-existing
mc mkdir veritas/$BUCKET_NAME/templates --ignore-existing
mc mkdir veritas/$BUCKET_NAME/assets --ignore-existing

# Set public policy
cat > /tmp/policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::veritas-reports/*"]
    }
  ]
}
EOF

mc policy set-json /tmp/policy.json veritas/$BUCKET_NAME

echo "✅ MinIO setup completed!"
echo "🌐 Access: http://$MINIO_HOST/minio/$BUCKET_NAME/"
echo "📂 Structure: projects/{id}/reports/, executions/, evidence/, templates/"

rm -f /tmp/policy.json
