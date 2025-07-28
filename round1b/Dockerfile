# Stage 1: Download the model
FROM python:3.9-slim as downloader

RUN pip install sentence-transformers==2.7.0
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('/model')"


# Stage 2: Final application image
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Create directories for input, output, and the model
RUN mkdir -p /app/input /app/output /app/model

# Copy requirements and install dependencies
COPY requirements.txt .
# Ensure we install the CPU version of torch for compatibility and size
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the model from the downloader stage
COPY --from=downloader /model /app/model

# Copy the main processing script
COPY analyze_docs.py .

# Command to run the script
CMD ["python", "analyze_docs.py"]