FROM python:3.9-slim

# Install system dependencies including GUI support
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-tk \
    python3-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxtst6 \
    libfontconfig1 \
    libxrandr2 \
    libasound2-dev \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create user with same UID as pi user (1000) and add to dialout group
RUN groupadd -g 20 dialout && \
    useradd -u 1000 -g 1000 -G dialout -s /bin/bash -m pi

# Copy application code
COPY . .

# Set environment variables for GUI
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["bash"]
