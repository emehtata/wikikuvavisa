# Use an official Python image from the Docker Hub
FROM python:3-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app .

# Expose port 5500
EXPOSE 5500

# Command to run the application
CMD ["python", "app.py"]

