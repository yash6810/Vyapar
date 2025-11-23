# Dockerfile for the RAG service

FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install git and other build dependencies
RUN apt-get update && apt-get install -y git

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# This will also cache the sentence-transformers model
RUN pip install --no-cache-dir -r requirements.txt

# Copy the RAG service and the knowledge base
COPY backend/rag_service.py .
COPY knowledge_base ./knowledge_base

# Expose the port the app runs on
EXPOSE 8003

# Run the application
CMD ["uvicorn", "rag_service:app", "--host", "0.0.0.0", "--port", "8003"]
