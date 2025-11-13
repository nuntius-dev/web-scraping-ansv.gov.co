#!/bin/bash

# Crear directorio de logs si no existe
mkdir -p /app/logs

# Imprimir zona horaria configurada
echo "Zona horaria configurada: $(date)"
echo "Iniciando servicio de descarga automática ANSV..."
echo "El script se ejecutará todos los días a las 6:00 AM"

# Iniciar cron en foreground
echo "Iniciando cron..."
cron && tail -f /app/logs/cron.log