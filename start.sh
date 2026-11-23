#!/bin/sh
set -e

export API_URL="http://127.0.0.1:8001"

echo "Checking ChromaDB..."
python -c "from app.vectorstore import get_collection, store_chunks; collection = get_collection(); print('Existing chunks:', collection.count()); store_chunks() if collection.count() == 0 else print('Database already initialized.')"

echo "Configuring Nginx..."
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "Starting application services..."
exec supervisord -n -c /etc/supervisor/conf.d/ayushmansathi.conf
