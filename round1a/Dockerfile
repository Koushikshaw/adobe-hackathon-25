# Specify the platform to ensure AMD64 compatibility [cite: 57]
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory
WORKDIR /app

# Create directories for input and output volumes 
RUN mkdir -p /app/input /app/output

# Copy dependency list and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main processing script
COPY process_pdfs.py .

# Command to run the script when the container starts
CMD ["python", "process_pdfs.py"]