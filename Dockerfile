FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# --- SECCIÓN CORREGIDA ---
# Instalar Firefox-ESR (que sí es compatible con arm64)
RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*
# --- FIN DE LA SECCIÓN CORREGIDA ---

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar script de Python
COPY ansv_scraper.py .
# Copiar script de cron
COPY crontab /etc/cron.d/ansv-cron

# Dar permisos al archivo cron
RUN chmod 0644 /etc/cron.d/ansv-cron

# Aplicar el cron job
# (Se añade un 'echo' para forzar la línea nueva al final del archivo,
#  lo cual es un requisito de crontab)
RUN echo "" >> /etc/cron.d/ansv-cron \
    && crontab /etc/cron.d/ansv-cron

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Volumen para persistir datos
VOLUME ["/app/data"]

# Ejecutar cron en foreground
ENTRYPOINT ["/entrypoint.sh"]
