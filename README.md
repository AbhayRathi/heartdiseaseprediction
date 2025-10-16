# Reddit Playhouse AI Agent

## Project Overview
This project implements an autonomous Reddit agent designed to browse specified subreddits, identify posts related to social gatherings and meeting new people, and automatically respond to them. The agent promotes Playhouse AI, leveraging advanced LLM capabilities for human-like and context-aware interactions.

## Key Features
*   **Intelligent Browsing:** Monitors multiple subreddits for relevant posts.
*   **LLM-Powered Responses:** Utilizes Google Gemini to generate empathetic, diverse, and human-like responses.
*   **Retrieval-Augmented Generation (RAG):** Selects relevant phrases from `response_phrases.txt` based on post content to inform LLM responses.
*   **Persona-Driven Interactions:** Introduces Playhouse AI with specific personas (study buddy, AI peer, recommender, personalizable twin).
*   **Style Mimicry:** Learns and adapts its response style from previously gathered human posts.
*   **Proxy Management:** Implements time-based rotation of paid proxies to ensure robust and continuous operation, avoiding IP bans and rate limits.
*   **Rate Limiting & Duplicate Prevention:** Adheres to Reddit API guidelines by managing reply frequency and avoiding duplicate replies to the same post.
*   **Continuous Data Gathering:** Collects and stores relevant post data in `gathered_post_data.txt` for analysis and LLM training.
*   **Containerized Deployment:** Designed for deployment via Docker containers, facilitating easy cloud hosting on platforms like Azure.

## Local Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd heartdiseaseprediction
```

### 2. Create and Activate a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Reddit API Credentials (praw.ini)
Create a file named `praw.ini` in the `heartdiseaseprediction` directory with your Reddit API credentials.
```ini
[DEFAULT]
# This section defines credentials for your Reddit bot.
# Obtain these from: https://www.reddit.com/prefs/apps
# Create a 'script' type app.
client_id=<YOUR_REDDIT_CLIENT_ID>
client_secret=<YOUR_REDDIT_CLIENT_SECRET>
username=<YOUR_REDDIT_USERNAME>
password=<YOUR_REDDIT_PASSWORD>
# user_agent should be unique and identify your bot.
# Format: <platform>:<app ID>:<version string> (by u/<your Reddit username>)
user_agent=playhouse_ai_agent:v1.0 (by u/yourredditusername)
```
**Important:** Replace the placeholder values with your actual Reddit app details and username.

### 5. Configure Proxies (proxies.txt)
If you are using paid residential proxies (e.g., Oxylabs), create a file named `proxies.txt` in the `heartdiseaseprediction` directory. Each proxy should be on a new line in the format:
```
http://username:password@proxy_address:port
```
**Example (Oxylabs):**
```
http://customer-oxylabs-username:customer-oxylabs-password@pr.oxylabs.io:7777
http://customer-oxylabs-username:customer-oxylabs-password@pr.oxylabs.io:7778
# ... add all your proxies here
```
**Note:** You will need to replace `customer-oxylabs-username`, `customer-oxylabs-password`, `pr.oxylabs.io`, and `7777` with your actual Oxylabs credentials and proxy details. The agent will read these and rotate through them.

### 6. Set Google Gemini API Key
The Google Gemini API key is read from an environment variable. Set it before running the script:
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```
**Important:** Replace `YOUR_GEMINI_API_KEY` with your actual Gemini API key.

### 7. Run the Agent Locally
After setting up all configurations, you can run the agent:
```bash
python3 reddit_browser.py
```

## Azure Deployment (Containerized)

This section outlines the steps to deploy your Reddit agent as a Docker container to Azure. We will primarily focus on Azure Container Instances (ACI) for simplicity or Azure Kubernetes Service (AKS) for more complex, scalable deployments.

### 1. Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
*   [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and configured with your Azure account.
*   An Azure Subscription.

### 2. Build the Docker Image
Navigate to the `heartdiseaseprediction` directory and build your Docker image:
```bash
docker build -t reddit-playhouse-agent .
```

### 3. Create an Azure Container Registry (ACR)
An ACR is a private Docker registry in Azure.
```bash
az group create --name MyResourceGroup --location eastus
az acr create --resource-group MyResourceGroup --name myredditagentacr --sku Basic
```
Log in to your ACR:
```bash
az acr login --name myredditagentacr
```

### 4. Tag and Push the Docker Image to ACR
Tag your local image with your ACR login server and push it:
```bash
docker tag reddit-playhouse-agent myredditagentacr.azurecr.io/reddit-playhouse-agent:latest
docker push myredditagentacr.azurecr.io/reddit-playhouse-agent:latest
```

### 5. Deploy to Azure Container Instances (ACI)
ACI is suitable for simple, single container deployments.
```bash
az container create \
    --resource-group MyResourceGroup \
    --name reddit-agent-container \
    --image myredditagentacr.azurecr.io/reddit-playhouse-agent:latest \
    --cpu 1 \
    --memory 1.5 \
    --restart-policy Always \
    --environment-variables \
        "REDDIT_CLIENT_ID=<YOUR_REDDIT_CLIENT_ID>" \
        "REDDIT_CLIENT_SECRET=<YOUR_REDDIT_CLIENT_SECRET>" \
        "REDDIT_USERNAME=<YOUR_REDDIT_USERNAME>" \
        "REDDIT_PASSWORD=<YOUR_REDDIT_PASSWORD>" \
        "REDDIT_USER_AGENT=playhouse_ai_agent:v1.0 (by u/yourredditusername)" \
        "GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>" \
        "PROXY_USER=<OXYLABS_USERNAME>" \
        "PROXY_PASS=<OXYLABS_PASSWORD>" \
        "PROXY_HOST=<OXYLABS_PROXY_ADDRESS>" \
        "PROXY_PORT=<OXYLABS_PROXY_PORT>" \
    --acr-login-server myredditagentacr.azurecr.io \
    --acr-username <ACR_USERNAME> \
    --acr-password <ACR_PASSWORD>
```
**Important Environment Variables for Azure Deployment:**
When deploying to Azure, you will set the following as environment variables for your container instead of using `praw.ini` and `proxies.txt` directly.
*   `REDDIT_CLIENT_ID`: Your Reddit application client ID.
*   `REDDIT_CLIENT_SECRET`: Your Reddit application client secret.
*   `REDDIT_USERNAME`: Your Reddit bot's username.
*   `REDDIT_PASSWORD`: Your Reddit bot's password.
*   `REDDIT_USER_AGENT`: A unique user agent string for your bot.
*   `GEMINI_API_KEY`: Your Google Gemini API key.
*   `PROXY_USER`: Your Oxylabs proxy username.
*   `PROXY_PASS`: Your Oxylabs proxy password.
*   `PROXY_HOST`: The host address of your Oxylabs proxy (e.g., `pr.oxylabs.io`).
*   `PROXY_PORT`: The port of your Oxylabs proxy (e.g., `7777`).

**Note on ACI:** You will need to retrieve the ACR username and password using `az acr credential show --name myredditagentacr`.

### 6. Monitoring (Optional but Recommended)
You can view container logs in the Azure portal or using the CLI:
```bash
az container logs --resource-group MyResourceGroup --name reddit-agent-container
```

## Important Project Files
*   `reddit_browser.py`: The main script for the Reddit agent.
*   `praw.ini`: Reddit API credentials (for local use).
*   `proxies.txt`: List of proxy servers (for local use, awaiting Oxylabs update).
*   `response_phrases.txt`: A collection of pre-defined response phrases used by the LLM.
*   `gathered_post_data.txt`: Stores data from relevant Reddit posts for LLM style mimicry.
*   `requirements.txt`: Python dependencies.
*   `Dockerfile`: Defines the Docker image for the agent.

## Troubleshooting
*   **`407 Proxy Authentication Required`:** Ensure your proxy credentials (username, password) are correct and that your IP is whitelisted (if required by your proxy provider, e.g., Oxylabs). This error usually indicates an issue with the proxy service itself, not the code.
*   **`prawcore.exceptions.RequestException` / Network Errors:** Could be due to incorrect proxy setup, network issues, or Reddit API rate limits. Check proxy connectivity and `praw.ini` settings.
*   **`ModuleNotFoundError`:** Ensure your virtual environment is activated and all dependencies from `requirements.txt` are installed.
*   **LLM Response Issues:** Verify `GEMINI_API_KEY` is correctly set and the LLM service is accessible.
