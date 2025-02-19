# Use the official Python image from the Docker Hub
FROM python:3.10

FROM --platform=linux/arm64 python:3.7-alpine

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY ./app ./app

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]