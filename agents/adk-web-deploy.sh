#!/bin/bash
# This script translates the steps from cloudbuild.yaml to a bash script.

# Exit immediately if a command exits with a non-zero status.
set -e
export MCP_TOOLBOX_URL=$(gcloud run services describe toolbox --region us-central1 --format "value(status.url)")
export PROJECT_ID=$(gcloud config list --format 'value(core.project)')
export DB_PASS='pword'
export VERTEX_AI_ENDPOINT_ID=''

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID environment variable is not set."
  exit 1
fi

# Define the image tag
IMAGE_TAG="us-central1-docker.pkg.dev/$PROJECT_ID/adk/adk-web-ui-agent-bug-assist-vertexai-endpoint:latest"

# Step 1: Build the Docker image
echo "Building the Docker image..."
docker build \
  --tag "$IMAGE_TAG" \
  . \
  --file Dockerfile

# Step 2: Push the image to Google Artifact Registry
echo "Pushing the image to Artifact Registry..."
docker push "$IMAGE_TAG"

echo "Deployment script finished successfully."
gcloud run deploy adk-web-ui-vertexai-endpoint \
   --image=$IMAGE_TAG \
   --region=us-central1 \
   --allow-unauthenticated \
   --cpu=4 \
   --memory=2Gi \
   --network=default \
   --subnet=default \
   --vpc-egress=private-ranges-only \
   --set-env-vars=VERTEX_AI_ENDPOINT_ID=$VERTEX_AI_ENDPOINT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=TRUE,MCP_TOOLBOX_URL=$MCP_TOOLBOX_URL
