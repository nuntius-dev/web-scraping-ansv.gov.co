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
# Instalar Google Chrome (con el método moderno sin apt-key)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
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
RUN crontab /etc/cron.d/ansv-cron

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Volumen para persistir datos
VOLUME ["/app/data"]

# Ejecutar cron en foreground
ENTRYPOINT ["/entrypoint.sh"]
