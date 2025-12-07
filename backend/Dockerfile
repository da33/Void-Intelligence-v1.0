# Use official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies (FFmpeg is required for audio transcoding)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port internal to the container (Zeabur uses 8080 or sets PORT env)
EXPOSE 8000

# Command to run the application
# We use shell form to allow expansion of $PORT if Zeabur sets it, defaulting to 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
