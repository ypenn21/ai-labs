

# Running the ADK Agents 🤖

Before proceeding, ensure you have already deployed your Gemma 3 model to either GKE or Vertex AI by following one of the primary notebooks.

The instructions below correspond to the deployment option you chose.


1. Set Up Environment Variables

Create a file named `.env` inside the gke-agent directory. This file will configure the agent to communicate with your local, port-forwarded model endpoint.


The `.env` file should look like the file content as below:

```bash
# Choose Model Backend: 0 -> Gemini API key, 1 -> Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=True

# Gemini API key backend config
GOOGLE_API_KEY=YOUR_VALUE_HERE

# Vertex AI backend config
GOOGLE_CLOUD_PROJECT= YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION= YOUR_VALUE_HERE

# Only for model hosted on vertexai endpoint
VERTEX_AI_ENDPOINT_ID=YOUR_VALUE_HERE

# Model details only for models hosted on gke
AGENT_MODE=GKE
MODEL_NAME = YOUR_VALUE_HERE
MODEL_VERSION= YOUR_VALUE_HERE

```

2. Deploy the ADK Agent to Cloud Run

Set up environment variables:
```
GOOGLE_CLOUD_PROJECT=YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
GOOGLE_GENAI_USE_VERTEXAI=True
# Only for model hosted on vertexai endpoint
VERTEX_AI_ENDPOINT_ID=YOUR_VALUE_HERE

# Model details only for models hosted on gke
AGENT_MODE=GKE
MODEL_NAME = YOUR_VALUE_HERE
MODEL_VERSION= YOUR_VALUE_HERE
```

Deployment command:
Under 'agents' folder, run:

```
IMAGE_TAG="us-central1-docker.pkg.dev/$PROJECT_ID/adk/adk-web-ui-agent-bug-assist-vertexai-endpoint:latest"
gcloud run deploy adk-web-ui-vertexai-agent \
   --image=$IMAGE_TAG \
   --region=$GOOGLE_CLOUD_LOCATION \
   --allow-unauthenticated \
   --source . \
   --port 8080 \
   --cpu=4 \
   --memory=2Gi \
   --network=default \
   --subnet=default \
   --vpc-egress=private-ranges-only \
   --set-env-vars=VERTEX_AI_ENDPOINT_ID=$VERTEX_AI_ENDPOINT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=TRUE,MCP_TOOLBOX_URL=$MCP_TOOLBOX_URL
```

Follow the url provided, select 'vertexai_agent' from the drop down window, then you can test the agent.
