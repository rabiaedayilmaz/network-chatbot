FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8501

CMD ["bash", "-c", "chmod +x /app/start.sh && /app/start.sh"]