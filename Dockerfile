# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY src /app

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose internal port 700 (Optional, for documentation)
EXPOSE 7001

ENV PYTHONUNBUFFERED=1

# Set the default command
CMD ["python", "/app/server.py"]
