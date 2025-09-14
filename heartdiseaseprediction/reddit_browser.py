"""
This script implements a Reddit agent that browses specified subreddits, identifies
posts related to social gatherings and meeting new people, and automatically
responds to them. The agent promotes Playhouse AI, optionally incorporating
snippets from an external website in its responses. It includes features for
proxy management and prevents duplicate replies to the same post.
"""

import praw
import os
import random
import requests
from bs4 import BeautifulSoup
import time
import itertools
import google.generativeai as genai

# --- Configuration (praw.ini) ---
# Make sure your praw.ini file is in this directory with your credentials:
# [DEFAULT]
# username = YOUR_REDDIT_USERNAME
# password = YOUR_REDDIT_PASSWORD
# client_id = YOUR_CLIENT_ID
# client_secret = YOUR_CLIENT_SECRET

# --- Gemini LLM Configuration ---
# It is highly recommended to set your Gemini API key as an environment variable (e.g., GEMINI_API_KEY)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set. LLM responses will not be available.")

# Global iterator for proxy rotation
proxy_cycle = None

# Initializes and returns a Reddit instance.
def initialize_reddit():
    """
    Initializes and returns a Reddit instance using credentials from praw.ini.

    It attempts to connect to Reddit using the 'DEFAULT' profile defined in praw.ini.
    If the initialization fails, an error message is printed, and None is returned.

    Returns:
        praw.Reddit: An initialized Reddit instance if successful, None otherwise.
    """
    try:
        reddit = praw.Reddit('DEFAULT')
        print("Reddit instance initialized successfully.")
        return reddit
    except Exception as e:
        print(f"Error initializing Reddit: {e}")
        return None

# Loads response phrases from a text file.
def load_response_phrases(file_path):
    """
    Loads response phrases from a text file.

    Each line in the specified file is treated as a separate response phrase.
    Empty lines and lines containing only whitespace are ignored.

    Args:
        file_path (str): The path to the text file containing response phrases.

    Returns:
        list: A list of strings, where each string is a response phrase.
              Returns an empty list if the file is not found or an error occurs.
    """
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

# Loads proxy servers from a text file.
def load_proxies(file_path):
    """
    Loads proxy server URLs from a text file.

    Each line in the specified file is treated as a separate proxy server URL.
    Lines starting with '#' (comments) and empty lines are ignored.
    Examples of valid proxy formats:
    - http://user:pass@ip:port
    - socks5://ip:port

    Args:
        file_path (str): The path to the text file containing proxy server URLs.

    Returns:
        list: A list of strings, where each string is a proxy server URL.
              Returns an empty list if the file is not found or an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        print(f"Loaded {len(proxies)} proxies from {file_path}.")
        return proxies
    except FileNotFoundError:
        print(f"Error: Proxies file not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error loading proxies: {e}")
        return []

# Returns the next proxy in a cycling list.
def get_next_proxy():
    """
    Retrieves the next proxy from the global `proxy_cycle` iterator.

    This function is designed to cycle through a list of proxies provided
    in `proxies.txt`. If `proxy_cycle` is not initialized or if all proxies
    have been exhausted (in a non-cycling scenario, though here it cycles indefinitely),
    it handles the case gracefully.

    Returns:
        str or None: The next proxy URL as a string, or None if `proxy_cycle`
                     is not initialized.
    """
    global proxy_cycle
    if proxy_cycle:
        try:
            return next(proxy_cycle)
        except StopIteration:
            # This case should ideally not be reached with itertools.cycle
            print("All proxies exhausted, restarting cycle.")
            return None
    return None

# Loads IDs of posts that have already been replied to.
def load_replied_posts(file_path):
    """
    Loads a set of submission IDs from a file that the agent has already replied to.

    This prevents the agent from replying multiple times to the same post,
    ensuring a more human-like and less spammy behavior.

    Args:
        file_path (str): The path to the file storing replied post IDs.

    Returns:
        set: A set of strings, where each string is a submission ID.
             Returns an empty set if the file is not found or an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            replied_ids = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(replied_ids)} previously replied posts from {file_path}.")
        return replied_ids
    except FileNotFoundError:
        print(f"Replied posts file not found at {file_path}. Starting with empty set.")
        return set()
    except Exception as e:
        print(f"Error loading replied posts: {e}")
        return set()

# Saves an ID to the list of replied posts.
def save_replied_post(file_path, submission_id):
    """
    Saves a submission ID to the file of replied posts.

    This function appends the given submission ID to the specified file,
    marking it as "replied" so the agent doesn't interact with it again.

    Args:
        file_path (str): The path to the file storing replied post IDs.
        submission_id (str): The ID of the Reddit submission to save.
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(submission_id + '\n')
        print(f"Saved replied post ID: {submission_id}")
    except Exception as e:
        print(f"Error saving replied post ID {submission_id}: {e}")

# Returns a random response phrase.
def get_random_response(phrases):
    """
    Selects and returns a random response phrase from a provided list.

    Args:
        phrases (list): A list of strings, where each string is a possible response.

    Returns:
        str: A randomly selected response phrase. If the `phrases` list is empty,
             it returns a default greeting.
    """
    if phrases:
        return random.choice(phrases)
    return "Hello there!" # Default response if no phrases are loaded

# Fetches and extracts readable text from a URL.
def get_web_content(url, proxy=None):
    """
    Fetches content from a given URL and extracts readable text using BeautifulSoup.

    It simulates a web browser request by including a User-Agent header.
    If a proxy is provided, the request is routed through that proxy.
    Error handling is included for network issues and HTTP errors.

    Args:
        url (str): The URL of the web page to fetch.
        proxy (str, optional): The proxy server URL to use for the request (e.g., "http://ip:port").
                               Defaults to None, meaning no proxy is used.

    Returns:
        str or None: A cleaned string containing the extracted readable text from the web page,
                     or None if an error occurs during fetching or processing.
    """
    try:
        # Simulate a browser request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        # Configure proxies if provided
        proxies_config = {
            "http": proxy,
            "https": proxy,
        } if proxy else None

        # Make the HTTP GET request with a timeout
        response = requests.get(url, headers=headers, proxies=proxies_config, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements to clean up the text
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        
        # Get all text, split into lines, strip whitespace, and join into a single clean string
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

# Generates a response using the Gemini LLM.
def generate_llm_response(prompt, model_name="models/gemini-1.5-pro"):
    """
    Generates a response using the Google Gemini LLM.

    Ensures the GEMINI_API_KEY is configured before attempting to generate a response.

    Args:
        prompt (str): The prompt to send to the LLM.
        model_name (str, optional): The name of the Gemini model to use. Defaults to "models/gemini-1.5-pro".

    Returns:
        str or None: The generated text response from the LLM, or None if an error occurs
                     or the API key is not configured.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not configured. Cannot generate LLM response.")
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return None

# Generates a response, optionally including content from a URL.
def generate_agent_response(response_phrases, url=None, snippet_length=200, proxy=None, use_llm=False, llm_prompt_prefix=""):
    """
    Generates a complete response string for the Reddit agent.

    This function can either combine a randomly selected base phrase with an optional
    snippet of text fetched from a given URL, or it can use an LLM for more advanced responses.

    Args:
        response_phrases (list): A list of base phrases for the response (used if use_llm is False).
        url (str, optional): An optional URL to fetch additional content from.
                             Defaults to None.
        snippet_length (int, optional): The maximum length of the snippet to
                                        extract from the web content. Defaults to 200.
        proxy (str, optional): The proxy server URL to use for fetching web content.
                               Defaults to None.
        use_llm (bool, optional): If True, an LLM will be used to generate the response.
                                  Defaults to False.
        llm_prompt_prefix (str, optional): A prefix to add to the prompt sent to the LLM.
                                           Defaults to an empty string.

    Returns:
        str: The full agent response.
    """
    final_response = ""

    if use_llm:
        llm_input_text = llm_prompt_prefix
        if url:
            web_text = get_web_content(url, proxy=proxy)
            if web_text:
                llm_input_text += f"\n\nHere is some context from a webpage: {web_text[:1000].strip()}...\n\n"
        
        if llm_input_text:
            llm_response = generate_llm_response(llm_input_text)
            if llm_response:
                final_response = llm_response
            else:
                print("LLM response failed, falling back to basic response.")
                final_response = get_random_response(response_phrases)
        else:
            final_response = get_random_response(response_phrases)
    else:
        base_response = get_random_response(response_phrases)
        
        if url:
            web_text = get_web_content(url, proxy=proxy)
            if web_text:
                snippet = web_text[:snippet_length].strip() + "..." if len(web_text) > snippet_length else web_text.strip()
                final_response = f"{base_response}\n\nHere's something I found: \"{snippet}\"\n\n(Source: {url})"
            else:
                final_response = base_response
        else:
            final_response = base_response

    return final_response

# Main function to run the Reddit agent.
def run_reddit_agent(reddit_instance, subreddits, keywords, response_phrases, replied_posts_file, replied_posts_set, external_link_for_agent_response=None, use_llm=False, llm_prompt_prefix=""):
    """
    Executes the main logic of the Reddit agent.

    It iterates through a list of specified subreddits, fetches new posts,
    and checks if post titles or bodies contain any of the defined keywords.
    If a relevant post is found and the agent hasn't replied to it before,
    it generates a response (optionally with web content) and posts it.
    Includes rate limiting and proxy rotation for robustness.

    Args:
        reddit_instance (praw.Reddit): An initialized PRAW Reddit instance.
        subreddits (list): A list of subreddit names (e.g., ['social', 'meetup']) to browse.
        keywords (list): A list of keywords to search for in post titles and bodies.
        response_phrases (list): A list of phrases to use for generating responses.
        replied_posts_file (str): Path to the file storing IDs of already replied posts.
        replied_posts_set (set): A set containing IDs of posts already replied to.
        external_link_for_agent_response (str, optional): A URL to fetch content from
                                                           for richer responses. Defaults to None.
        use_llm (bool, optional): If True, an LLM will be used to generate the response.
                                  Defaults to False.
        llm_prompt_prefix (str, optional): A prefix to add to the prompt sent to the LLM.
                                           Defaults to an empty string.
    """
    if not reddit_instance:
        print("Reddit instance not available. Agent cannot run.")
        return
    
    print("\n--- Starting Reddit Agent Cycle ---")
    current_proxy = get_next_proxy() # Get initial proxy for this cycle or None if no proxies

    for subreddit_name in subreddits:
        try:
            subreddit = reddit_instance.subreddit(subreddit_name)
            print(f"Browsing r/{subreddit_name} for new posts...")
            
            # Fetch the newest 15 posts from the subreddit
            for submission in subreddit.new(limit=15):
                title = submission.title.lower()
                selftext = submission.selftext.lower() # Post body
                
                # Check if any keyword is present in the title or selftext
                if any(keyword in title or keyword in selftext for keyword in keywords):
                    # Check if the agent has already replied to this post
                    if submission.id not in replied_posts_set:
                        print(f"  [DETECTED] Relevant post: '{submission.title}' (ID: {submission.id}) by u/{submission.author}")
                        
                        # Generate the agent's response
                        llm_input_context = f"User post title: {submission.title}\nUser post body: {submission.selftext}"
                        full_llm_prompt = f"{llm_prompt_prefix}\n\n{llm_input_context}"
                        
                        agent_response = generate_agent_response(response_phrases,
                                                                 url=external_link_for_agent_response,
                                                                 proxy=current_proxy,
                                                                 use_llm=use_llm,
                                                                 llm_prompt_prefix=full_llm_prompt)
                        
                        print(f"  [RESPONSE  ] -> {agent_response[:100]}...") # Print first 100 chars of response for logging
                        
                        # --- Actual posting logic ---
                        try:
                            submission.reply(agent_response) # Post the reply to Reddit
                            print(f"  [ACTION    ] Replied to post ID: {submission.id}")
                            replied_posts_set.add(submission.id) # Add to in-memory set
                            save_replied_post(replied_posts_file, submission.id) # Save to file for persistence
                        except praw.exceptions.APIException as e:
                            # Handle Reddit API specific errors (e.g., rate limits, invalid scopes)
                            print(f"  [ERROR     ] Failed to reply to post {submission.id}: {e}")
                        except Exception as e:
                            # Catch any other unexpected errors during replying
                            print(f"  [ERROR     ] An unexpected error occurred while replying to post {submission.id}: {e}")
                        
                        # IMPORTANT: Adhere to Reddit's rate limits. Adjust sleep time as needed.
                        # Reddit generally limits 1 reply per 10 minutes per user/bot.
                        time.sleep(600) # Pause to avoid hitting Reddit API rate limits (10 minutes = 600 seconds)
                    else:
                        print(f"  [SKIPPED   ] Already replied to post ID: {submission.id}")

            # Optional: Add a delay between subreddit checks to be polite and avoid hammering the API
            time.sleep(5)

        except Exception as e:
            print(f"Error running agent for r/{subreddit_name}: {e}")
            # If an error occurs (e.g., network issue with current proxy), try switching proxy
            current_proxy = get_next_proxy()
            if not current_proxy:
                print("No more proxies available. Agent stopping.")
                break # Exit the loop if no more proxies
            print(f"Switched to next proxy: {current_proxy}")

    print("--- Reddit Agent Cycle Finished ---")

if __name__ == "__main__":
    # Ensure the script runs from its directory to find configuration files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Current working directory changed to: {os.getcwd()}")

    # --- Proxy Initialization ---
    proxies_file = 'proxies.txt'
    available_proxies = load_proxies(proxies_file)
    if available_proxies:
        # Create a cycling iterator for proxies for continuous rotation
        proxy_cycle = itertools.cycle(available_proxies)
    else:
        print("No proxies loaded. Proceeding without proxies for Reddit API and web fetching.")

    # --- Reddit API Initialization ---
    reddit_instance = initialize_reddit()

    # Configure Reddit API to use the first available proxy if proxies are loaded
    if reddit_instance and available_proxies:
        first_proxy = get_next_proxy()
        if first_proxy:
            # PRAW allows injecting a custom requests.Session for proxy support
            session = requests.Session()
            session.proxies = {"http": first_proxy, "https": first_proxy}
            reddit_instance._core._requestor._http = session
            print(f"Reddit API configured to use proxy: {first_proxy}")

    if reddit_instance:
        # --- Gemini Model Verification --- (Temporarily added for debugging, now removed)
        # if GEMINI_API_KEY:
        #     try:
        #         genai.configure(api_key=GEMINI_API_KEY)
        #         print("\n--- Available Gemini Models ---")
        #         for m in genai.list_models():
        #             if "generateContent" in m.supported_generation_methods:
        #                 print(f"  - {m.name}")
        #         print("-------------------------------")
        #     except Exception as e:
        #         print(f"Error listing Gemini models: {e}")
        # else:
        #     print("GEMINI_API_KEY not set, skipping Gemini model listing.")

        # Load response phrases from the configuration file
        response_file = 'response_phrases.txt'
        response_list = load_response_phrases(response_file)

        # Load previously replied post IDs to prevent duplicate replies
        replied_posts_filename = 'replied_posts.txt'
        replied_posts_set = load_replied_posts(replied_posts_filename)

        # --- Agent Configuration ---
        # List of subreddits the agent will monitor
        target_subreddits = ['social', 'meetup', 'CasualConversation', 'NeedAFriend']
        # Keywords to search for in post titles and bodies to determine relevance
        search_keywords = ['gathering', 'meet new people', 'social event', 'hangout', 'lonely', 'friends', 'introduce myself', 'Playhouse AI']
        # Optional external URL to fetch content from for enriching responses
        external_url_for_agent_response = "https://playhouse-ai.world/"
        # Configuration for LLM usage
        USE_LLM_FOR_RESPONSES = True  # Set to True to enable LLM-based responses
        # Prefix for the LLM prompt, guiding its response style and purpose
        LLM_PROMPT_PREFIX = "You are a friendly Reddit bot named Playhouse AI Agent. Your goal is to gently introduce Playhouse AI in conversations about social gatherings or meeting new people. Keep your responses natural, helpful, and concise (under 150 words). Avoid being overly promotional. Base your responses on the context provided, if any. If no context, make a general comment or question about Playhouse AI relevant to social interactions."

        # Print initial agent configuration for user's awareness
        print("\n--- Initializing Reddit Agent with following configuration ---")
        print(f"Subreddits: {target_subreddits}")
        print(f"Keywords: {search_keywords}")
        print(f"Response phrases loaded: {len(response_list) > 0}")
        if external_url_for_agent_response:
            print(f"Using external link for responses: {external_url_for_agent_response}")
        if USE_LLM_FOR_RESPONSES:
            print(f"Using LLM for responses: {USE_LLM_FOR_RESPONSES}")
            print(f"LLM Prompt Prefix: {LLM_PROMPT_PREFIX[:100]}...")
        print("----------------------------------------------------------")

        # Start the main agent loop
        run_reddit_agent(reddit_instance, target_subreddits, search_keywords, response_list, replied_posts_filename, replied_posts_set, external_url_for_agent_response, USE_LLM_FOR_RESPONSES, LLM_PROMPT_PREFIX)

    else:
        print("Failed to initialize Reddit. Please check praw.ini credentials and ensure the file exists.")
