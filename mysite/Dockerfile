FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
# Make entrypoint script executable
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]