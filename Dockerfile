# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy python files
COPY *.py .

# Create a directory for input/output files
RUN mkdir -p /data

# Set the working directory
WORKDIR /data

# Set the entrypoint
ENTRYPOINT ["python", "/app/variant_annotator.py"]

# Default command shows help
CMD ["--help"]

