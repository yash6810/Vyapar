# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the intent_classifier.py
COPY backend/intent_classifier.py .

# Expose the port the app runs on
EXPOSE 8002

# Run the application
CMD ["uvicorn", "intent_classifier:app", "--host", "0.0.0.0", "--port", "8002"]
