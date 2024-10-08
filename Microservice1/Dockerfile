# Use a smaller base image
FROM python:3.9-slim


# Set the working directory
WORKDIR /app

# Copy only the requirements file first for better caching
COPY requirements.txt ./

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY app.py ./
COPY index.html ./templates/

# Expose port 80
EXPOSE 80


CMD ["python", "./app.py"]
