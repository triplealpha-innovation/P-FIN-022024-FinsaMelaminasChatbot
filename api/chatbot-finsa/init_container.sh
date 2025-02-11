#!/bin/bash
echo "Iniciando ssh......................"
service ssh start

if [ "$APP_ENV" = "production" ]; then
    echo "Iniciando uvicorn chatbot Finsa en modo $APP_ENV con gunicorn..........."
    NUM_WORKERS=2
    exec gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --workers $NUM_WORKERS
else
    echo "Iniciando uvicorn chatbot Finsa en modo desarrollo con uvicorn............"
    exec uvicorn main:app --reload --host 0.0.0.0 --port 80
fi