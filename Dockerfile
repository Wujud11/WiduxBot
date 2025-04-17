
# Use Python 3.11 base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 9001

# Run both API server and Twitch bot
CMD ["sh", "-c", "uvicorn api_server:app --host 0.0.0.0 --port 9001 & python3 main.py"]
