# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory to /app
WORKDIR /app

# Copy Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Install Tesseract OCR and Thai language support
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-tha

# Copy the .env file
COPY .env /app/

# Copy the current directory contents into the container at /app
COPY /app/ /app

# Expose the port that your FastAPI application will run on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]