# Use the official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install build tools and dependencies
RUN apt-get update && \
    apt-get install -y build-essential python3-dev && \
    apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install pip requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Initialize models
RUN bash init_models.sh

# Expose port 5000
EXPOSE 5000

# Run the application
ENTRYPOINT ["bash", "run_api.sh"]
