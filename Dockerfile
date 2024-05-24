# Base image with Python and Java (needed for PySpark)
FROM python:3.12-slim as base

# Install Packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip ffmpeg curl espeak && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir /app
WORKDIR /app

COPY requirements.txt run.py entrypoint.sh config.yaml ./
COPY app/transcriber app/transcriber
COPY app/utils app/utils

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Give execution rights to the entrypoint script and ensure it's owned by chronos
RUN chmod +x /app/entrypoint.sh

# Set the script as the entry point
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
