import praw
import os
import random
import requests
from bs4 import BeautifulSoup
import time # Added for sleep functionality

# --- Configuration (praw.ini) ---
# Make sure your praw.ini file is in this directory with your credentials:
# [DEFAULT]
# username = YOUR_REDDIT_USERNAME
# password = YOUR_REDDIT_PASSWORD
# client_id = YOUR_CLIENT_ID
# client_secret = YOUR_CLIENT_SECRET

def initialize_reddit():
    """Initializes and returns a Reddit instance using praw.ini."""
    try:
        reddit = praw.Reddit('DEFAULT')
        print("Reddit instance initialized successfully.")
        return reddit
    except Exception as e:
        print(f"Error initializing Reddit: {e}")
        return None

def load_response_phrases(file_path):
    """Loads response phrases from a text file, one phrase per line."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(phrases)} response phrases from {file_path}.")
        return phrases
    except FileNotFoundError:
        print(f"Error: Response phrases file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error loading response phrases: {e}")
        return []

def get_random_response(phrases):
    """Returns a random response phrase from the loaded list."""
    if phrases:
        return random.choice(phrases)
    return "Hello there!" # Default response if no phrases are loaded

def get_web_content(url):
    """
    Fetches content from a URL and extracts readable text using BeautifulSoup.
    Returns a string of extracted text, or None if an error occurs.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for phrase in ' '.join(lines).split("  "))
        cleaned_text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"Successfully extracted content from {url}")
        return cleaned_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing content from {url}: {e}")
        return None

def generate_agent_response(response_phrases, url=None, snippet_length=200):
    """
    Generates a response, optionally including content from a URL.
    Combines a random pre-defined phrase with a snippet from the web content.
    """
    base_response = get_random_response(response_phrases)
    
    if url:
        web_text = get_web_content(url)
        if web_text:
            snippet = web_text[:snippet_length].strip() + "..." if len(web_text) > snippet_length else web_text.strip()
            return f"{base_response}\n\nHere's something I found: \"{snippet}\"\n\n(Source: {url})"
    
    return base_response

def run_reddit_agent(reddit_instance, subreddits, keywords, response_phrases, external_link_for_response=None):
    """
    Main function to run the Reddit agent: browses subreddits, detects relevant posts,
    and simulates generating responses.
    """
    if not reddit_instance:
        print("Reddit instance not available. Agent cannot run.")
        return
    
    print("\n--- Starting Reddit Agent Cycle ---")
    for subreddit_name in subreddits:
        try:
            subreddit = reddit_instance.subreddit(subreddit_name)
            print(f"Browsing r/{subreddit_name} for new posts...")
            
            # Stream new posts (or use .hot(), .top() for initial scan)
            # Use limit to control how many posts to check per cycle
            for submission in subreddit.new(limit=15):
                title = submission.title.lower()
                selftext = submission.selftext.lower() # Post body
                
                # Check for keywords in title or selftext
                if any(keyword in title or keyword in selftext for keyword in keywords):
                    print(f"  [DETECTED] Relevant post: '{submission.title}' (ID: {submission.id}) by u/{submission.author}")
                    
                    # Generate a response for the detected post
                    agent_response = generate_agent_response(response_phrases, url=external_link_for_response)
                    print(f"  [RESPONSE  ] -> {agent_response[:100]}...") # Print first 100 chars of response
                    
                    # --- Placeholder for actual posting logic ---
                    # try:
                    #     # submission.reply(agent_response)
                    #     print(f"  [ACTION    ] Replied to post ID: {submission.id}")
                    # except praw.exceptions.APIException as e:
                    #     print(f"  [ERROR     ] Failed to reply to post {submission.id}: {e}")
                    # time.sleep(10) # Avoid rate limiting (adjust as needed)

                # else:
                #     print(f"  [SKIPPED   ] No keywords found in: {submission.title}")

            # Optional: Add a delay between subreddit checks to be polite
            time.sleep(5) 

        except Exception as e:
            print(f"Error running agent for r/{subreddit_name}: {e}")
    
    print("--- Reddit Agent Cycle Finished ---")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Current working directory changed to: {os.getcwd()}")

    reddit_instance = initialize_reddit()
    if reddit_instance:
        response_file = 'response_phrases.txt'
        response_list = load_response_phrases(response_file)

        # --- Agent Configuration ---
        # These are the subreddits and keywords provided by the user
        target_subreddits = ['social', 'meetup', 'CasualConversation', 'NeedAFriend']
        search_keywords = ['gathering', 'meet new people', 'social event', 'hangout', 'lonely', 'friends', 'introduce myself', 'Playhouse AI']
        external_url_for_agent_response = "https://playhouse-ai.world/" # This URL will be used for responses

        print("\n--- Initializing Reddit Agent with following configuration ---")
        print(f"Subreddits: {target_subreddits}")
        print(f"Keywords: {search_keywords}")
        print(f"Response phrases loaded: {len(response_list) > 0}")
        if external_url_for_agent_response: 
            print(f"Using external link for responses: {external_url_for_agent_response}")
        print("----------------------------------------------------------")

        run_reddit_agent(reddit_instance, target_subreddits, search_keywords, response_list, external_url_for_agent_response)

    else:
        print("Failed to initialize Reddit. Please check praw.ini credentials.")
