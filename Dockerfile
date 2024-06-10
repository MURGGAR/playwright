# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variable to avoid prompts
ARG DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xvfb \
    libxcomposite1 \
    libxdamage1 \
    libatk1.0-0 \
    libasound2 \
    libdbus-1-3 \
    libnspr4 \
    libgbm1 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libnss3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies and Playwright browsers
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps

# Copy the rest of the application code into the container
COPY . .

# Set environment variables for Playwright and Flask
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & python app.py"]
