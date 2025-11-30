#!/bin/bash
# This script translates the steps from cloudbuild.yaml to a bash script.

# Exit immediately if a command exits with a non-zero status.
set -e
export PROJECT_ID=$(gcloud config list --format 'value(core.project)')
export VERTEX_AI_ENDPOINT_ID='1234567890'
export GOOGLE_CLOUD_LOCATION=us-central1
export MCP_TOOLBOX_URL=$(gcloud run services describe toolbox --region $GOOGLE_CLOUD_LOCATION --format "value(status.url)")
export AGENT_MODE=VertexAI
#if AGENT_MODE is GKE, set the following variables will set the model name and version. If AGENT_MODE is VertexAI, the following variables will not matter
export MODEL_NAME='gemma-3-11b'
export MODEL_VERSION='latest'

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID environment variable is not set."
  exit 1
fi

# Define the image tag
IMAGE_TAG="${GOOGLE_CLOUD_LOCATION}-docker.pkg.dev/${PROJECT_ID}/adk/adk-web-ui-agent-bug-assist-vertexai-endpoint:latest"
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
   --region=$GOOGLE_CLOUD_LOCATION \
   --allow-unauthenticated \
   --cpu=4 \
   --memory=2Gi \
   --network=default \
   --subnet=default \
   --vpc-egress=private-ranges-only \
   --set-env-vars=AGENT_MODE=$AGENT_MODE,VERTEX_AI_ENDPOINT_ID=$VERTEX_AI_ENDPOINT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=TRUE,MCP_TOOLBOX_URL=$MCP_TOOLBOX_URL,MODEL_NAME=$MODEL_NAME,MODEL_VERSION=$MODEL_VERSION
