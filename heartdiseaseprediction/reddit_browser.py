import praw
import os

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
    # Ensure praw.ini is in the correct directory for PRAW to find it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Current working directory changed to: {os.getcwd()}")

    reddit = initialize_reddit()
    if reddit:
        # Example usage: Provide your desired subreddits here
        my_subreddits = ['social', 'meetup', 'CasualConversation', 'NeedAFriend'] # Example subreddits
        browse_subreddits(reddit, my_subreddits)
    else:
        print("Failed to initialize Reddit. Please check praw.ini credentials.")
