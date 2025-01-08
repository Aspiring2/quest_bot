# Use the official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000
# Установка gunicorn
RUN pip install gunicorn

# Command to run the app
CMD ["gunicorn", "questbot.wsgi:application", "--bind", "0.0.0.0:8000"]
