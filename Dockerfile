FROM python:3.12-slim-bullseye
 
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 


RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt  /app/
 
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]