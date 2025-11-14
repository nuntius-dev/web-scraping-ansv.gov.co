#!/bin/bash

# Crear directorio de logs y el archivo de log vacío
mkdir -p /app/logs
touch /app/logs/cron.log

echo "Zona horaria configurada: $(date)"
echo "Iniciando servicio de descarga automática ANSV..."

# Iniciar cron en segundo plano
echo "Iniciando cron... (tareas se ejecutarán en background)"
cron

# Iniciar la API de Flask en primer plano
# Esto mantendrá el contenedor vivo
echo "Iniciando API de Flask en http://0.0.0.0:8080..."
export FLASK_APP=ansv_scraper.py
export FLASK_RUN_PORT=8080
export FLASK_RUN_HOST=0.0.0.0
flask run
