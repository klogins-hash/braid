#!/bin/bash
# Build and Deploy MCP Server Docker Images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry.com"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
DOCKER_DIR="docker"
K8S_DIR="k8s"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker and try again."
        exit 1
    fi
    
    print_status "Docker $(docker --version | cut -d' ' -f3 | sed 's/,//') found"
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_status "Docker daemon is running"
    
    # Check Docker Compose (optional)
    if command_exists docker-compose; then
        print_status "Docker Compose $(docker-compose --version | cut -d' ' -f3 | sed 's/,//') found"
    else
        print_warning "Docker Compose not found (optional for standalone usage)"
    fi
    
    # Check kubectl (optional)
    if command_exists kubectl; then
        print_status "kubectl $(kubectl version --client --short 2>/dev/null | cut -d' ' -f3) found"
    else
        print_warning "kubectl not found (optional for Kubernetes deployment)"
    fi
}

# Function to build MCP server images
build_mcp_images() {
    print_section "Building MCP Server Docker Images"
    
    # Create build directory structure if it doesn't exist
    mkdir -p "$DOCKER_DIR/mcp-servers"
    
    local images=("perplexity" "xero" "notion")
    local build_success=0
    local build_total=${#images[@]}
    
    for service in "${images[@]}"; do
        print_status "Building $service MCP server image..."
        
        local dockerfile_path="$DOCKER_DIR/mcp-servers/$service/Dockerfile"
        local image_name="$DOCKER_REGISTRY/mcp-$service:$IMAGE_TAG"
        
        if [ ! -f "$dockerfile_path" ]; then
            print_error "Dockerfile not found: $dockerfile_path"
            continue
        fi
        
        # Build the image
        if docker build -t "$image_name" -f "$dockerfile_path" "$DOCKER_DIR/mcp-servers/$service/"; then
            print_status "✅ Successfully built $image_name"
            ((build_success++))
            
            # Tag with latest if not already latest
            if [ "$IMAGE_TAG" != "latest" ]; then
                docker tag "$image_name" "$DOCKER_REGISTRY/mcp-$service:latest"
                print_status "   Tagged as latest"
            fi
        else
            print_error "❌ Failed to build $image_name"
        fi
    done
    
    print_status "Built $build_success/$build_total MCP server images successfully"
    
    if [ $build_success -eq 0 ]; then
        print_error "No images were built successfully"
        exit 1
    fi
}

# Function to push images to registry
push_images() {
    print_section "Pushing Images to Registry"
    
    local images=("perplexity" "xero" "notion")
    local push_success=0
    local push_total=${#images[@]}
    
    # Check if we can push to registry
    if [ "$DOCKER_REGISTRY" = "your-registry.com" ]; then
        print_warning "Using default registry placeholder. Set DOCKER_REGISTRY environment variable for actual push."
        print_warning "Skipping push to registry."
        return 0
    fi
    
    for service in "${images[@]}"; do
        local image_name="$DOCKER_REGISTRY/mcp-$service:$IMAGE_TAG"
        
        print_status "Pushing $image_name..."
        
        if docker push "$image_name"; then
            print_status "✅ Successfully pushed $image_name"
            ((push_success++))
            
            # Push latest tag if different
            if [ "$IMAGE_TAG" != "latest" ]; then
                if docker push "$DOCKER_REGISTRY/mcp-$service:latest"; then
                    print_status "   Also pushed latest tag"
                fi
            fi
        else
            print_error "❌ Failed to push $image_name"
        fi
    done
    
    print_status "Pushed $push_success/$push_total images successfully"
}

# Function to generate Docker Compose override
generate_compose_override() {
    print_section "Generating Docker Compose Override"
    
    local override_file="$DOCKER_DIR/docker-compose.override.yml"
    
    cat > "$override_file" << EOF
version: '3.8'

services:
  perplexity-mcp:
    image: $DOCKER_REGISTRY/mcp-perplexity:$IMAGE_TAG
    
  xero-mcp:
    image: $DOCKER_REGISTRY/mcp-xero:$IMAGE_TAG
    
  notion-mcp:
    image: $DOCKER_REGISTRY/mcp-notion:$IMAGE_TAG
EOF
    
    print_status "Generated Docker Compose override: $override_file"
}

# Function to update Kubernetes manifests
update_k8s_manifests() {
    print_section "Updating Kubernetes Manifests"
    
    local k8s_file="$K8S_DIR/mcp-deployment.yaml"
    local k8s_updated="$K8S_DIR/mcp-deployment-updated.yaml"
    
    if [ ! -f "$k8s_file" ]; then
        print_warning "Kubernetes manifest not found: $k8s_file"
        return 0
    fi
    
    # Update image references in Kubernetes manifests
    sed "s|your-registry/perplexity-mcp:latest|$DOCKER_REGISTRY/mcp-perplexity:$IMAGE_TAG|g; \
         s|your-registry/xero-mcp:latest|$DOCKER_REGISTRY/mcp-xero:$IMAGE_TAG|g; \
         s|your-registry/notion-mcp:latest|$DOCKER_REGISTRY/mcp-notion:$IMAGE_TAG|g" \
        "$k8s_file" > "$k8s_updated"
    
    print_status "Updated Kubernetes manifest: $k8s_updated"
}

# Function to run deployment tests
test_deployment() {
    print_section "Testing Deployment"
    
    print_status "Starting test deployment with Docker Compose..."
    
    # Test with Docker Compose
    if [ -f "$DOCKER_DIR/docker-compose.mcp.yml" ]; then
        cd "$DOCKER_DIR"
        
        # Start services in background
        if docker-compose -f docker-compose.mcp.yml up -d; then
            print_status "Test deployment started"
            
            # Wait for services to be ready
            sleep 30
            
            # Check service health
            local services=("perplexity-mcp" "xero-mcp" "notion-mcp")
            local healthy_services=0
            
            for service in "${services[@]}"; do
                if docker-compose -f docker-compose.mcp.yml ps "$service" | grep -q "Up"; then
                    print_status "✅ $service is running"
                    ((healthy_services++))
                else
                    print_error "❌ $service is not running"
                fi
            done
            
            # Cleanup
            print_status "Stopping test deployment..."
            docker-compose -f docker-compose.mcp.yml down
            
            print_status "Test complete: $healthy_services/${#services[@]} services were healthy"
        else
            print_error "Failed to start test deployment"
        fi
        
        cd ..
    else
        print_warning "Docker Compose file not found, skipping deployment test"
    fi
}

# Function to cleanup old images
cleanup_images() {
    print_section "Cleaning Up Old Images"
    
    local images=("perplexity" "xero" "notion")
    
    for service in "${images[@]}"; do
        # Remove dangling images
        local dangling=$(docker images -f "dangling=true" -f "reference=$DOCKER_REGISTRY/mcp-$service" -q)
        if [ -n "$dangling" ]; then
            print_status "Removing dangling images for mcp-$service..."
            docker rmi $dangling
        fi
        
        # Keep only the last 3 tags (excluding latest)
        local old_images=$(docker images "$DOCKER_REGISTRY/mcp-$service" --format "table {{.Tag}}\t{{.ID}}" | \
                          grep -v "TAG\|latest" | \
                          tail -n +4 | \
                          awk '{print $2}')
        
        if [ -n "$old_images" ]; then
            print_status "Removing old images for mcp-$service..."
            echo "$old_images" | xargs -r docker rmi
        fi
    done
    
    print_status "Image cleanup completed"
}

# Main function
main() {
    print_section "MCP Server Docker Build and Deploy"
    
    echo "This script will:"
    echo "  1. Build Docker images for all MCP servers"
    echo "  2. Push images to registry (if configured)"
    echo "  3. Generate deployment configurations"
    echo "  4. Test deployment (optional)"
    echo ""
    
    # Parse command line arguments
    local PUSH_IMAGES=false
    local RUN_TESTS=false
    local CLEANUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --push)
                PUSH_IMAGES=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            --tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --push              Push images to registry"
                echo "  --test              Run deployment tests"
                echo "  --cleanup           Clean up old images"
                echo "  --registry REGISTRY Set Docker registry (default: your-registry.com)"
                echo "  --tag TAG           Set image tag (default: latest)"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run build process
    check_prerequisites
    build_mcp_images
    
    if [ "$PUSH_IMAGES" = true ]; then
        push_images
    fi
    
    generate_compose_override
    update_k8s_manifests
    
    if [ "$RUN_TESTS" = true ]; then
        test_deployment
    fi
    
    if [ "$CLEANUP" = true ]; then
        cleanup_images
    fi
    
    print_section "Build Complete!"
    
    echo -e "${GREEN}✅ MCP server images build completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy with Docker Compose: cd docker && docker-compose -f docker-compose.mcp.yml up -d"
    echo "  2. Deploy with Kubernetes: kubectl apply -f k8s/mcp-deployment-updated.yaml"
    echo "  3. Update your agent to connect to the deployed MCP servers"
    echo ""
    echo "Built images:"
    for service in "perplexity" "xero" "notion"; do
        echo "  - $DOCKER_REGISTRY/mcp-$service:$IMAGE_TAG"
    done
}

# Run main function with all arguments
main "$@"