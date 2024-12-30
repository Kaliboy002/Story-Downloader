# Use a slim Python image
FROM python:3.10-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the bot token environment variable (can also be set in Railway settings)
ENV BOT_TOKEN=your_bot_token_here

# Expose port (optional for non-bot services)
EXPOSE 5000

# Command to run the bot
CMD ["python", "bot.py"]
