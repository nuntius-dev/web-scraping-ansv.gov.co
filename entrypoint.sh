#!/bin/bash

# Crear directorio de logs y el archivo de log vacío
mkdir -p /app/logs
touch /app/logs/cron.log

# Imprimir zona horaria configurada
echo "Zona horaria configurada: $(date)"
echo "Iniciando servicio de descarga automática ANSV..."
echo "El script se ejecutará todos los días a las 6:00 AM"

# Iniciar cron en segundo plano
echo "Iniciando cron..."
cron

# Iniciar 'tail' en primer plano.
# Esto es lo que mantendrá el contenedor vivo.
# Ahora tendrá éxito porque el archivo 'cron.log' ya existe.
tail -f /app/logs/cron.log
