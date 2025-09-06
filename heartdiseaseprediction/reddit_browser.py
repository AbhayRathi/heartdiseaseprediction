import praw
import os
import random
import requests # Added for web fetching
from bs4 import BeautifulSoup # Added for HTML parsing

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
        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        
        # Get text, strip whitespace, and join lines
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        # Remove empty lines and join with a space
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

def browse_subreddits(reddit_instance, subreddits_to_browse):
    """
    Browses through a list of subreddits and prints the titles of new posts.
    This is a basic browsing function without advanced filtering or response logic.
    """
    if not reddit_instance:
        print("Reddit instance not available. Cannot browse subreddits.")
        return

    print("\n--- Starting Subreddit Browsing ---")
    for sub_name in subreddits_to_browse:
        try:
            subreddit = reddit_instance.subreddit(sub_name)
            print(f"\nBrowsing r/{sub_name} for new posts (Top 5):")
            for submission in subreddit.new(limit=5): # Get the 5 newest posts
                print(f"  - {submission.title}")
        except Exception as e:
            print(f"Error browsing r/{sub_name}: {e}")

    print("--- Finished Subreddit Browsing ---")

if __name__ == "__main__":
    # Ensure praw.ini and response_phrases.txt are in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Current working directory changed to: {os.getcwd()}")

    reddit = initialize_reddit()
    if reddit:
        # Load response phrases
        response_file = 'response_phrases.txt'
        response_list = load_response_phrases(response_file)

        # Example usage of response generation:
        print("\n--- Testing Response Generation ---")
        # Test with just a random phrase
        print(f"Agent Response (no URL): {generate_agent_response(response_list)}")

        # Test with a URL
        test_url = "https://www.google.com" # Replace with a real URL for testing
        print(f"\nAgent Response (with URL): {generate_agent_response(response_list, url=test_url)}")
        
        # Example usage: Provide your desired subreddits here
        my_subreddits = ['social', 'meetup', 'CasualConversation', 'NeedAFriend'] # Example subreddits
        browse_subreddits(reddit, my_subreddits)
    else:
        print("Failed to initialize Reddit. Please check praw.ini credentials.")
