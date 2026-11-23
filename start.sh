#!/bin/sh
set -e

export API_URL="http://127.0.0.1:8001"

echo "Configuring Nginx..."
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "Starting application services..."
exec supervisord -n -c /etc/supervisor/conf.d/ayushmansathi.conf
