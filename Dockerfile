# Use official Python base image
FROM python:3.13-slim

# Create a non-root user
RUN useradd -m appuser

# Create project folder inside container and set as working directory
WORKDIR /biomimetics_app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install git (needed if requirements.txt uses git+ URLs)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files from build context into container's working dir
COPY . ./

# Fix permissions: give appuser ownership of the project directory
RUN chown -R appuser:appuser /biomimetics_app

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Command to run the app
CMD ["python", "run.py"]

