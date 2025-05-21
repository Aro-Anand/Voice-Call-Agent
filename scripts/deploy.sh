# scripts/deploy.sh
#!/bin/bash
# Deployment script for LiveKit Call Agent

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker could not be found. Please install Docker before continuing."
    exit 1
fi

# Check if docker-compose is available (for local deployments)
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose could not be found. Using Docker directly."
    USE_COMPOSE=false
else
    USE_COMPOSE=true
fi

# Environment check
if [ -z "$1" ]; then
    ENV="local"
else
    ENV="$1"
fi

echo "Deploying to $ENV environment..."

# Build the image
echo "Building Docker image..."
docker build -t livekit-call-agent:latest .

if [ "$ENV" = "local" ]; then
    # Local deployment using docker-compose
    if [ "$USE_COMPOSE" = true ]; then
        echo "Starting services with Docker Compose..."
        docker-compose up -d
    else
        echo "Starting services with Docker..."
        docker run -d --name livekit-call-agent \
            --env-file .env \
            -p 8080:8080 \
            livekit-call-agent:latest
    fi
elif [ "$ENV" = "production" ]; then
    # Production deployment steps would go here
    # This could push to a registry, deploy to a cloud service, etc.
    echo "Production deployment not implemented yet."
    echo "You would typically push to a registry and deploy to your cloud provider."
else
    echo "Unknown environment: $ENV"
    echo "Supported environments: local, production"
    exit 1
fi

echo "Deployment completed."