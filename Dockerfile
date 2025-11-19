FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static/uploads/profile_photos \
    static/uploads/programs \
    static/uploads/passport_photos \
    static/resources

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
