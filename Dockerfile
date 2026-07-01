FROM python:3.12-slim

WORKDIR /app

# Install nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x run.sh

EXPOSE 10000

CMD ["./run.sh"]