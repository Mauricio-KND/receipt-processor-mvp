# Use an official Python image
FROM python:3.10-slim-bookworm

# Install system dependencies for Tesseract and OpenCV, and update all packages to latest security patches
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends tesseract-ocr libtesseract-dev libleptonica-dev \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port (Railway uses $PORT)
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app/web.py
ENV PYTHONUNBUFFERED=1

# Start the app (use $PORT for Railway)
CMD ["gunicorn", "app.web:app", "--bind", "0.0.0.0:8080"]