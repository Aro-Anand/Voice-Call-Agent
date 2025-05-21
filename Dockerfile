# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment to production
ENV NODE_ENV=production

# Expose the application port
EXPOSE 8080

# Start the application
CMD ["python", "main.py"]