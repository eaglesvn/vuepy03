# Use the specified Python and Node.js runtime as a parent image
FROM nikolaik/python-nodejs:python3.10-nodejs22-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app1/src \
    TZ=Asia/Bangkok

# Set the working directory
WORKDIR /ttsstt

# Create a non-root user and docker group, add eaglesvn to docker group
RUN useradd -m eaglesvn && \
    groupadd -r docker && \
    usermod -aG docker eaglesvn

# Install system dependencies and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl jq gcc libasound-dev libpq-dev libportaudio2 libportaudiocpp0 iputils-ping \
    portaudio19-dev libffi-dev python3-dev libevent-dev libevent-2.1-7 redis-tools \
    tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY .env /ttsstt
RUN pip install gunicorn[gevent] python-dotenv --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories and files, and set permissions
RUN mkdir -p /app1/src/gunicorn && mkdir -p /app1/logs && mkdir -p /app1/src/audio && \
    touch /app1/src/gunicorn/access.log /app1/src/gunicorn/error.log && \
    chown -R eaglesvn:docker /app1/src/gunicorn && \
    chmod -R 777 /app1/src/gunicorn && \
    touch /app1/logs/access.log /app1/logs/error.log && \
    chown -R eaglesvn:docker /app1/logs && \
    chmod -R 777 /app1/logs && \
    chown -R eaglesvn:docker /app1/src/audio && \
    chmod -R 777 /app1/src/audio

# Copy backend application code
COPY ./src /app1/src
RUN chown -R eaglesvn:docker /app1/src

# Switch to non-root user
USER eaglesvn

# Expose the application's port
EXPOSE 5001

# Run Gunicorn to start the application
CMD ["gunicorn", "--config", "/app1/src/gunicorn/gunicorn_config_ttsstt.py", "pyapp1_ttsstt:app1_mod_ttsstt"]
