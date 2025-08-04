# Use official Python runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy dependencies file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (including credentials.json if needed)
COPY . .

# Set the port (must match Flask app)
ENV PORT=10000
EXPOSE 10000

# Run the app
CMD ["python", "app.py"]
