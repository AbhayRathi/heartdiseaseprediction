import praw
import os
import random # Added for random response selection

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
            # Each line is considered a separate phrase
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
        
        if response_list:
            print(f"Sample random response: {get_random_response(response_list)}")

        # Example usage: Provide your desired subreddits here
        my_subreddits = ['social', 'meetup', 'CasualConversation', 'NeedAFriend'] # Example subreddits
        browse_subreddits(reddit, my_subreddits)
    else:
        print("Failed to initialize Reddit. Please check praw.ini credentials.")
