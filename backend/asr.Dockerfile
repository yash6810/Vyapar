# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the asr_service.py
COPY backend/asr_service.py .

# Expose the port the app runs on
EXPOSE 8001

# Run the application
CMD ["uvicorn", "asr_service:app", "--host", "0.0.0.0", "--port", "8001"]
