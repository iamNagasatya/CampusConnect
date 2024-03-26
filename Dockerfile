
# Specify the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose a port for the API
EXPOSE 8000
# Collect static files
RUN python manage.py collectstatic --noinput
# Specify the command to run the application
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "ProjectTime.wsgi"]
