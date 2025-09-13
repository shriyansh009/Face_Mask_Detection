# Use Python 3.10 (TensorFlow compatible)
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for OpenCV, Pillow, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port (Render expects $PORT)
EXPOSE 5000

# Start Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
