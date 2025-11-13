FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    cron \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# --- NUEVA SECCIÓN ---
# Instalar geckodriver para ARM64 (aarch64) manualmente
# ya que webdriver-manager falla en la detección de arquitectura
ENV GECKODRIVER_VERSION=v0.36.0
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux-aarch64.tar.gz" \
    && tar -xzf geckodriver-${GECKODRIVER_VERSION}-linux-aarch64.tar.gz \
    && rm geckodriver-${GECKODRIVER_VERSION}-linux-aarch64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/geckodriver
# --- FIN DE LA NUEVA SECCIÓN ---

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
# Dar permisos y forzar la línea nueva requerida por cron
RUN echo "" >> /etc/cron.d/ansv-cron \
    && chmod 0644 /etc/cron.d/ansv-cron \
    && crontab /etc/cron.d/ansv-cron

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Volumen para persistir datos
VOLUME ["/app/data"]

# Ejecutar script de inicio
ENTRYPOINT ["/entrypoint.sh"]
