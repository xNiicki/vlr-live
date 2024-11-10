FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the requirements
RUN pip install -r requirements.txt

# Copy the rest of the application code

COPY . .

# Expose the port the app runs on

EXPOSE 9091

# Start the application
CMD ["python", "main.py"]