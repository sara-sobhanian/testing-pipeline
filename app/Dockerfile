# Start from a lightweight Python base image
FROM python:3.11-slim

# Create a working directory inside the container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into /app
COPY . /app

# Expose port 5000 (Flask default)
EXPOSE 5000

# Define the entrypoint / command
CMD ["python", "app.py"]
