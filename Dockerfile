# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code from your current directory to the container at /app
COPY . .

# Make sure praw.ini is handled correctly (it should already be ignored by .gitignore in the main repo)
# And that you've filled in your credentials there.

# Define environment variables if needed (e.g., for non-praw.ini credentials)
# ENV REDDIT_USERNAME="your_username"
# ENV REDDIT_PASSWORD="your_password"

# Run reddit_browser.py when the container launches
CMD ["python3", "reddit_browser.py"]
