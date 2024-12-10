# Use an official Python runtime as a parent image
FROM python:3.12@sha256:f78ea8a345769eb3aa1c86cf147dfd68f1a4508ed56f9d7574e4687b02f44dd1

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Install git and curl
RUN apt-get update && \
    apt-get install -y git curl

# Set GitHub credentials as build arguments (to avoid hardcoding)
ARG GITHUB_TOKEN
ARG GITHUB_USERNAME
ENV GITHUB_TOKEN=${GITHUB_TOKEN}
ENV GITHUB_USERNAME=${GITHUB_USERNAME}

# Configure Git to use the Personal Access Token in a global .git-credentials file
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials && \
    git config --global user.email "app-builder@example.com" && \
    git config --global user.name "app-builder"

# Expose the port the app runs on
EXPOSE 5000

# Run Django's development server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000"]
