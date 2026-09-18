# Use the official Python 3.13 slim image to keep the container small
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install libgomp1, which is a required C-library for XGBoost on Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies with an extended timeout to prevent XGBoost drops
RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Copy the rest of your application code and ML models
COPY . .

# Cloud Run defaults to port 8080
EXPOSE 8080

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]