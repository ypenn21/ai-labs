

# Running the ADK Agents 🤖

Before proceeding, ensure you have already deployed your Gemma 3 model to either GKE or Vertex AI. As well as deploying [mcp-tool box and cloud sql](https://github.com/ypenn21/ai-labs/tree/main?tab=readme-ov-file#2---create-a-cloud-sql-postgres-instance).

The instructions below correspond to the deployment option you chose.


1. Set Up local dev environment for running ai agent web ui.

Use the file named [.env](.env). This file will configure the agent to communicate with your llm endpoint locally. Assuming mcp-tool box is running locally already if not refer to [Local Environment Setup](https://github.com/ypenn21/ai-labs/blob/main/README.md#local-environment)


The `.env` file should look like the file content as below:

```bash
# Choose Model Backend: 0 -> Gemini API key, 1 -> Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Gemini API key backend config
export GOOGLE_API_KEY=YOUR_VALUE_HERE

# Vertex AI backend config
export GOOGLE_CLOUD_PROJECT= YOUR_VALUE_HERE
export GOOGLE_CLOUD_LOCATION= YOUR_VALUE_HERE

# Only for model hosted on vertexai endpoint
export AGENT_MODE=VertexAI
export VERTEX_AI_ENDPOINT_ID=YOUR_VALUE_HERE

# Model details only for models hosted on gke
#export AGENT_MODE=GKE
export MODEL_NAME = YOUR_VALUE_HERE
export MODEL_VERSION= YOUR_VALUE_HERE

export PROJECT_ID=$(gcloud config list --format 'value(core.project)')
export VERTEX_AI_ENDPOINT_ID='1234567890'
export GOOGLE_CLOUD_LOCATION=us-central1
export MCP_TOOLBOX_URL=$(gcloud run services describe toolbox --region $GOOGLE_CLOUD_LOCATION --format "value(status.url)")

```

2. Deploy the ADK Agent to Cloud Run

Set up environment variables in the adk-web-deploy.sh script:
```
export PROJECT_ID=$(gcloud config list --format 'value(core.project)')
export VERTEX_AI_ENDPOINT_ID='1234567890'
export GOOGLE_CLOUD_LOCATION=us-central1
export MCP_TOOLBOX_URL=$(gcloud run services describe toolbox --region $GOOGLE_CLOUD_LOCATION --format "value(status.url)")
```
Deployment command assuming MCP_TOOLBOX is deployed. Set VERTEX_AI_ENDPOINT_ID & GOOGLE_CLOUD_LOCATION in the adk-web-deploy.sh script:
Under 'agents' folder, run:

```
vi adk-web-deploy.sh
./adk-web-deploy.sh
```

Follow the url provided, select 'adk_bug_ticket_agent' from the drop down window, then you can test the agent.
