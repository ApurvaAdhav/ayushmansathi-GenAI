
FROM python:3.12-slim

WORKDIR /app

RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/ayushmansathi.conf

EXPOSE 10000

CMD ["sh", "/app/start.sh"]
