# Reddit Social Gathering Agent (within heartdiseaseprediction)

This project contains a Python-based Reddit agent designed to browse specific subreddits, identify posts related to social gatherings and meeting new people, and automatically respond to them. The agent is configured to advocate for Playhouse AI, optionally incorporating snippets from an external website in its responses. It also includes proxy management for distributed operation.

## Features

*   **Reddit API Integration:** Connects to Reddit using the PRAW library.
*   **Configurable Subreddits & Keywords:** Easily specify which subreddits to monitor and what keywords to search for in post titles and bodies.
*   **Human-like Responses:** Generates replies by selecting random phrases from a local text file (`response_phrases.txt`).
*   **External Content Integration:** Can fetch content from a specified URL and include snippets in its replies.
*   **Duplicate Reply Prevention:** Tracks replied-to posts to avoid spamming the same submission.
*   **Proxy Management:** Supports loading and rotating through a list of HTTP/HTTPS/SOCKS proxies to distribute requests and bypass rate limits.
*   **Docker Support:** Includes a `Dockerfile` for easy containerization and deployment to cloud platforms.
*   **Python Virtual Environment:** Manages project dependencies cleanly.

## Getting Started

Follow these instructions to set up and run the Reddit agent.

### 1. Prerequisites

*   Python 3.9+ installed on your system.
*   `pip` (Python package installer).
*   A Reddit account.
*   A Reddit API application (type: `script`) configured on [Reddit's App Preferences](https://www.reddit.com/prefs/apps/).

### 2. Clone the Repository

First, navigate to your desired directory and clone this repository:

```bash
cd /Users/abhaysingh/personalProjects/heartdiseaseprediction
git clone https://github.com/AbhayRathi/heartdiseaseprediction.git
cd heartdiseaseprediction
```

### 3. Set up Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `.\venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Configuration

Before running the agent, you must configure your Reddit API credentials and optionally your proxies.

#### `praw.ini` (Reddit API Credentials)

Create a file named `praw.ini` in the root of this project (if it doesn't exist) and populate it with your Reddit API application credentials. **Keep this file secure and do NOT commit it to a public repository!**

Example `praw.ini`:

```ini
[DEFAULT]
username = YOUR_REDDIT_USERNAME
password = YOUR_REDDIT_PASSWORD
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
```

#### `proxies.txt` (Proxy List - Optional)

If you plan to use proxies, create a file named `proxies.txt` in the root of this project and list your proxy servers, one per line. The agent will cycle through these.

Example `proxies.txt`:

```
# Add your proxy servers here, one per line.
# Format: http://user:pass@ip:port or socks5://ip:port
http://myproxy.com:8080
http://user:pass@192.168.1.1:3128
socks5://localhost:9050
```

#### `response_phrases.txt` (Agent Responses)

This file contains the phrases your agent will use to construct its responses. Update it with messages advocating for Playhouse AI or asking questions about it. Each phrase should be on a new line.

### 5. Running the Agent

To run the Reddit agent locally:

1.  **Activate your virtual environment** (if not already active):
    ```bash
source venv/bin/activate # On Windows, use `.\venv\Scripts\activate`
    ```
2.  **Execute the main script:**
    ```bash
python3 reddit_browser.py
    ```

The agent will start browsing the configured subreddits and output its actions to the console. Actual replies will be posted if `praw.ini` is correctly configured and the agent detects relevant posts it hasn't replied to before.

### 6. Docker Deployment

To build a Docker image for your agent:

```bash
docker build -t reddit-playhouse-agent .
```

To run the agent in a Docker container (ensure your `praw.ini` and `proxies.txt` are bound as volumes or configured via environment variables in a real deployment):

```bash
docker run --name playhouse-reddit-bot -v $(pwd)/praw.ini:/app/praw.ini:ro -v $(pwd)/proxies.txt:/app/proxies.txt:ro reddit-playhouse-agent
```

*(Note: For production, consider using Docker Compose, Kubernetes, or specific cloud container services for robust deployment and secrets management.)*

## Future Enhancements

*   **Advanced LLM Integration:** Replace rule-based response generation with a fine-tuned Large Language Model (LLM) for more contextual and human-like replies.
*   **Robust Logging:** Implement Python's `logging` module for better tracking of agent activity and errors.
*   **Scheduled Runs:** Integrate with cloud schedulers (e.g., AWS CloudWatch Events, Google Cloud Scheduler) or cron jobs for automated, periodic execution.
*   **Database for Replied Posts:** Replace `replied_posts.txt` with a more robust database solution (e.g., SQLite, PostgreSQL) for persistent tracking across restarts and scaling.
*   **Monitoring & Alerts:** Set up monitoring dashboards and alerts for agent health, reply count, and error rates.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. (Note: A `LICENSE` file does not yet exist and would need to be created if desired.)
