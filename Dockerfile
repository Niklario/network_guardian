FROM python:3.12-alpine

WORKDIR /app

COPY *.py /app/
COPY dashboard.html /app/dashboard.html

ENV PYTHONUNBUFFERED=1

CMD ["python3", "/app/main.py"]
