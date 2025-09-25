# Use Python base image
FROM python:3.11-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (optional)
RUN python manage.py collectstatic --noinput || true

# Expose Django port
EXPOSE 8000

# Run migrations + start Daphne (ASGI server)
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 campus_safety_platform.asgi:application"]
