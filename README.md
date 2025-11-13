# 📘 INSTRUCTIVO COMPLETO: Automatización ANSV con Docker en VPS

## 🎯 Objetivo
Desplegar un sistema automatizado que descargue diariamente a las 6:00 AM los datos de fotodetección de ANSV y los organice en archivos Excel mensuales con hojas diarias.

---

## 📋 Requisitos Previos

### 1. VPS/Servidor
- **RAM mínima**: 2 GB
- **Almacenamiento**: 10 GB libres
- **Sistema Operativo**: Ubuntu 20.04 o superior / Debian 11 o superior
- **Proveedores recomendados**:
  - DigitalOcean (desde $6/mes)
  - Linode (desde $5/mes)
  - AWS Lightsail (desde $5/mes)
  - Contabo (desde €4/mes)

### 2. Acceso al Servidor
- Acceso SSH con usuario root o sudo

---

## 🚀 OPCIÓN 1: Despliegue con Docker (RECOMENDADO)

### Paso 1: Conectarse al VPS

```bash
ssh root@TU_IP_DEL_VPS
# o si tienes usuario con sudo:
ssh tu_usuario@TU_IP_DEL_VPS
```

### Paso 2: Actualizar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 3: Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar instalación
docker --version
```

### Paso 4: Instalar Docker Compose

```bash
sudo apt install docker-compose -y

# Verificar instalación
docker-compose --version
```

### Paso 5: Crear Estructura de Proyecto

```bash
# Crear directorio del proyecto
mkdir -p ~/ansv-scraper
cd ~/ansv-scraper

# Crear subdirectorios
mkdir -p data logs
```

### Paso 6: Crear Archivos del Proyecto

#### 6.1 Crear `ansv_scraper.py`

```bash
nano ansv_scraper.py
```

Copia el contenido del artifact "Script PRODUCCIÓN: Descarga Diaria Excel ANSV" y pégalo aquí.

Guarda con: `Ctrl + O`, `Enter`, luego `Ctrl + X`

#### 6.2 Crear `requirements.txt`

```bash
nano requirements.txt
```

Copia:
```
selenium==4.15.2
webdriver-manager==4.0.1
openpyxl==3.1.2
pandas==2.1.3
```

Guarda y cierra.

#### 6.3 Crear `Dockerfile`

```bash
nano Dockerfile
```

Copia el contenido del artifact "Dockerfile para ANSV Scraper" y pégalo aquí.

Guarda y cierra.

#### 6.4 Crear `docker-compose.yml`

```bash
nano docker-compose.yml
```

Copia el contenido del artifact "docker-compose.yml" y pégalo aquí.

Guarda y cierra.

#### 6.5 Crear `crontab`

```bash
nano crontab
```

Copia el contenido del artifact "crontab" y pégalo aquí.

Guarda y cierra.

#### 6.6 Crear `entrypoint.sh`

```bash
nano entrypoint.sh
```

Copia el contenido del artifact "entrypoint.sh" y pégalo aquí.

Guarda y cierra.

### Paso 7: Verificar Estructura

```bash
ls -la
```

Deberías ver:
```
ansv_scraper.py
requirements.txt
Dockerfile
docker-compose.yml
crontab
entrypoint.sh
data/
logs/
```

### Paso 8: Construir y Ejecutar el Contenedor

```bash
# Construir la imagen (toma 5-10 minutos)
docker-compose build

# Iniciar el contenedor
docker-compose up -d
```

### Paso 9: Verificar que Está Funcionando

```bash
# Ver logs del contenedor
docker-compose logs -f

# Ver estado del contenedor
docker-compose ps

# Ver logs de cron
tail -f logs/cron.log
```

### Paso 10: Probar Ejecución Manual (Opcional)

```bash
# Ejecutar el script manualmente para probar
docker-compose exec ansv-scraper python /app/ansv_scraper.py

# Ver archivos generados
ls -la data/
```

---

## 📊 Estructura de Archivos Generados

```
~/ansv-scraper/
├── data/
│   └── 2025/
│       ├── Enero.xlsx
│       ├── Febrero.xlsx
│       ├── ...
│       └── Octubre.xlsx
│           ├── Hoja: 2025-10-01
│           ├── Hoja: 2025-10-02
│           ├── Hoja: 2025-10-03
│           └── ...
└── logs/
    ├── ansv_202510.log
    └── cron.log
```

---

## 🔧 Comandos Útiles de Mantenimiento

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Reiniciar el contenedor
```bash
docker-compose restart
```

### Detener el contenedor
```bash
docker-compose down
```

### Ver logs del mes actual
```bash
tail -f logs/ansv_$(date +%Y%m).log
```

### Descargar archivos del VPS a tu Mac
```bash
# Desde tu Mac
scp -r root@TU_IP_DEL_VPS:~/ansv-scraper/data ~/Downloads/ansv_backup
```

### Actualizar el script
```bash
# Editar el script
nano ansv_scraper.py

# Reconstruir y reiniciar
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🛡️ OPCIÓN 2: Sin Docker (Instalación Directa en VPS)

Si prefieres no usar Docker:

### Paso 1-2: Igual que Opción 1

### Paso 3: Instalar Dependencias del Sistema

```bash
sudo apt update
sudo apt install -y python3 python3-pip wget unzip curl cron

# Instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
rm google-chrome-stable_current_amd64.deb
```

### Paso 4: Crear Proyecto

```bash
mkdir -p ~/ansv-scraper
cd ~/ansv-scraper
mkdir -p logs
```

### Paso 5: Crear y Copiar Script

```bash
nano ansv_scraper.py
```
Copia el script Python de producción.

### Paso 6: Instalar Librerías Python

```bash
pip3 install selenium webdriver-manager openpyxl pandas
```

### Paso 7: Configurar Cron

```bash
crontab -e
```

Agrega esta línea:
```
0 6 * * * cd ~/ansv-scraper && /usr/bin/python3 ansv_scraper.py >> logs/cron.log 2>&1
```

Guarda y cierra.

### Paso 8: Verificar Cron

```bash
crontab -l
```

---

## 🔍 Solución de Problemas

### El contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Chrome no funciona en modo headless
- Asegúrate de que el VPS tenga suficiente RAM (mínimo 2GB)
- El Dockerfile ya incluye las flags necesarias

### Los archivos no se están generando
```bash
# Verificar permisos
sudo chmod -R 755 ~/ansv-scraper/data

# Ejecutar manualmente para ver errores
docker-compose exec ansv-scraper python /app/ansv_scraper.py
```

### Cambiar la hora de ejecución
Edita el archivo `crontab`:
```bash
nano crontab
```

Cambia la línea:
- `0 6 * * *` = 6:00 AM
- `0 18 * * *` = 6:00 PM
- `30 9 * * *` = 9:30 AM

Luego:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 📱 Monitoreo y Alertas (Opcional)

### Configurar notificaciones por email
Puedes agregar al script Python:

```python
import smtplib
from email.mime.text import MIMEText

def enviar_alerta(mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = 'Alerta ANSV Scraper'
    msg['From'] = 'tu_email@gmail.com'
    msg['To'] = 'destino@gmail.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('tu_email@gmail.com', 'tu_password')
        server.send_message(msg)
```

---

## 💰 Costos Estimados

### Opción VPS Básico:
- **DigitalOcean**: $6/mes (1 vCPU, 1GB RAM, 25GB SSD)
- **Contabo**: €4/mes (4 vCPU, 8GB RAM, 50GB SSD)
- **AWS Lightsail**: $5/mes (1 vCPU, 1GB RAM, 40GB SSD)

### Recomendación:
**Contabo VPS S** - €4/mes (mejor relación precio/características)

---

## ✅ Checklist Final

- [ ] VPS contratado y accesible por SSH
- [ ] Docker y Docker Compose instalados
- [ ] Todos los archivos creados en el servidor
- [ ] Contenedor construido y ejecutándose
- [ ] Logs verificados sin errores
- [ ] Prueba manual exitosa
- [ ] Cron configurado para 6:00 AM

---

## 📞 Comandos de Resumen Rápido

```bash
# Ver estado
docker-compose ps

# Ver logs en vivo
docker-compose logs -f

# Ejecutar manualmente
docker-compose exec ansv-scraper python /app/ansv_scraper.py

# Descargar archivos
scp -r root@IP:~/ansv-scraper/data ~/Downloads/

# Reiniciar todo
docker-compose restart
```

---

## 🎉 ¡Listo!

Tu sistema está configurado para descargar automáticamente los datos de ANSV todos los días a las 6:00 AM.

Los archivos se organizarán así:
- **2025/Octubre.xlsx** con hojas por cada día del mes
- **2025/Noviembre.xlsx** (se creará automáticamente)
- **2026/Enero.xlsx** (cuando cambie el año)