# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY Pipfile* app.py /app/

# Install any needed packages specified in Pipfile.lock
RUN pipenv install --system --deploy

# Make port 8088 available to the world outside this container
EXPOSE 8088

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
