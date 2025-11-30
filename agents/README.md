

# Running the ADK Agents 🤖

Before proceeding, ensure you have already deployed your Gemma 3 model to either GKE or Vertex AI by following one of the primary notebooks.

The instructions below correspond to the deployment option you chose.


1. Set Up Environment Variables

Create a file named `.env` inside the gke-agent directory. This file will configure the agent to communicate with your local, port-forwarded model endpoint.


The `.env` file should look like the file content as below:

```bash
# Choose Model Backend: 0 -> Gemini API key, 1 -> Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=1

# Gemini API key backend config
GOOGLE_API_KEY=YOUR_VALUE_HERE

# Vertex AI backend config
GOOGLE_CLOUD_PROJECT= YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION= YOUR_VALUE_HERE

# Model details
MODEL_NAME = YOUR_VALUE_HERE
MODEL_VERSION= YOUR_VALUE_HERE

```

2. Run the ADK Agent locally

➡️ Open another terminal window, navigate back to the `agents` directory, and start the ADK web server.

 ```
 uv run adk web --port 8001
```
You can now access your agent's UI or API, which is running on http://localhost:8001.



## Agent for Gemma 3 on Vertex AI 

These steps will connect an ADK agent to the Gemma 3 model you deployed on a Vertex AI Endpoint.

First, navigate to the correct agent directory:

Bash
```
cd agents/vertexai-agent
```

1. Set Up Environment Variables
Create a file named `.env` inside the vertexai-agent directory. This file configures the agent with your Google Cloud project and Vertex AI endpoint details.

`.env` file with following keys:
```
# Choose Model Backend: 0 -> Gemini API key, 1 -> Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=1

# Gemini API key backend config
GOOGLE_API_KEY=YOUR_VALUE_HERE

# Vertex AI backend config
GOOGLE_CLOUD_PROJECT= YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION= YOUR_VALUE_HERE

# Model details
VERTEX_AI_ENDPOINT_ID = YOUR_VALUE_HERE
```
2. Run the ADK Agent locally

In your terminal (back to `agents`directory), start the ADK web server.

 Under `agent` folder, run
 ```
 uv run adk web --port 8002
```
3. Deploy the ADK Agent to Cloud Run

Set up environment variables:
```
export GOOGLE_CLOUD_PROJECT=YOUR_VALUE_HERE
export GOOGLE_CLOUD_LOCATION=us-central1 # Or your preferred location
export GOOGLE_GENAI_USE_VERTEXAI=True
export VERTEX_AI_ENDPOINT_ID=YOUR_VALUE_HERE
```

Deployment command:
Under 'agents' folder, run:

```
gcloud run deploy adk-web-ui-vertexai-agent \
   --image=us-central1-docker.pkg.dev/$PROJECT_ID/adk/adk-web-ui-agent-bug-assist:latest \
   --region=us-central1 \
   --allow-unauthenticated \
   --source . \
   --port 8080 \
   --cpu=4 \
   --memory=2Gi \
   --network=default \
   --subnet=default \
   --vpc-egress=private-ranges-only \
   --set-env-vars=VERTEX_AI_ENDPOINT_ID=2527670579629129728,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=TRUE,MCP_TOOLBOX_URL=$MCP_TOOLBOX_URL
```

Follow the url provided, select 'vertexai_agent' from the drop down window, then you can test the agent.
