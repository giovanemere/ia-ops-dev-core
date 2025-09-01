#!/bin/bash

# Load Docker credentials
source .docker-credentials

echo "🐳 IA-Ops Dev Core - Build and Push to Docker Hub"
echo "=================================================="

# Docker login
echo "🔐 Logging into Docker Hub..."
echo $DOCKER_TOKEN | docker login --username $DOCKER_USERNAME --password-stdin

if [ $? -ne 0 ]; then
    echo "❌ Docker login failed"
    exit 1
fi

echo "✅ Docker login successful"

# Build and push function
build_and_push() {
    local service_name=$1
    local dockerfile=$2
    local image_name=$3
    local context_dir=$4
    
    echo ""
    echo "🔨 Building $service_name..."
    
    # Build image
    docker build -f $dockerfile -t $DOCKER_USERNAME/$image_name:$VERSION -t $DOCKER_USERNAME/$image_name:latest $context_dir
    
    if [ $? -ne 0 ]; then
        echo "❌ Build failed for $service_name"
        return 1
    fi
    
    echo "✅ Build successful for $service_name"
    
    # Push images
    echo "📤 Pushing $service_name to Docker Hub..."
    
    docker push $DOCKER_USERNAME/$image_name:$VERSION
    docker push $DOCKER_USERNAME/$image_name:latest
    
    if [ $? -ne 0 ]; then
        echo "❌ Push failed for $service_name"
        return 1
    fi
    
    echo "✅ Push successful for $service_name"
    return 0
}

# Build all services
echo ""
echo "🏗️ Building all IA-Ops services..."

# Repository Manager
build_and_push "Repository Manager" "api/Dockerfile.repository" "$REPO_MANAGER_IMAGE" "api/"

# Task Manager  
build_and_push "Task Manager" "api/Dockerfile.task" "$TASK_MANAGER_IMAGE" "api/"

# Log Manager
build_and_push "Log Manager" "api/Dockerfile.log" "$LOG_MANAGER_IMAGE" "api/"

# DataSync Manager
build_and_push "DataSync Manager" "api/Dockerfile.datasync" "$DATASYNC_MANAGER_IMAGE" "api/"

# GitHub Runner Manager
build_and_push "GitHub Runner Manager" "api/Dockerfile.github-runner" "$GITHUB_RUNNER_IMAGE" "api/"

# TechDocs Builder
build_and_push "TechDocs Builder" "api/Dockerfile.techdocs" "$TECHDOCS_BUILDER_IMAGE" "api/"

# Swagger Portal
build_and_push "Swagger Portal" "api/Dockerfile.swagger" "$SWAGGER_PORTAL_IMAGE" "api/"

# Testing Portal
build_and_push "Testing Portal" "testing-portal/Dockerfile" "$TESTING_PORTAL_IMAGE" "testing-portal/"

echo ""
echo "📊 Build Summary"
echo "================"

# List built images
echo "🖼️ Built Images:"
docker images | grep $DOCKER_USERNAME | grep ia-ops

echo ""
echo "🎉 All services built and pushed successfully!"
echo ""
echo "🚀 Next Steps:"
echo "1. Test with: docker-compose -f docker-compose.production.yml up"
echo "2. Access Swagger Portal: http://localhost:8870"
echo "3. Access Testing Portal: http://localhost:18860"
echo ""
echo "📦 Docker Hub Images:"
echo "- $DOCKER_USERNAME/$REPO_MANAGER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$TASK_MANAGER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$LOG_MANAGER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$DATASYNC_MANAGER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$GITHUB_RUNNER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$TECHDOCS_BUILDER_IMAGE:latest"
echo "- $DOCKER_USERNAME/$SWAGGER_PORTAL_IMAGE:latest"
echo "- $DOCKER_USERNAME/$TESTING_PORTAL_IMAGE:latest"
