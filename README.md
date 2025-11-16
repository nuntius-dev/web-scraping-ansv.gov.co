# 📘 INSTRUCTIVO COMPLETO: Scraper Automatizado y API JSON de ANSV con Easypanel

## 🎯 Objetivo

Desplegar un sistema de dos componentes en un servidor VPS usando **Easypanel**:

1.  **Un Scraper Automatizado:** Descarga diariamente a las 6:00 AM (hora de Colombia) los datos de fotodetección de ANSV usando Selenium/Firefox.
2.  **Una API JSON:** Expone los datos descargados a través de una API web simple (construida con Flask), permitiendo el consumo de datos en formato JSON desde cualquier aplicación.

Este instructivo asume el despliegue en un servidor **ARM64 (aarch64)** (como los de Oracle Cloud, AWS Graviton, etc.).

-----

## 🛠️ Arquitectura Final del Proyecto

Este sistema utiliza un único contenedor Docker orquestado por Easypanel, pero ejecuta dos procesos de forma inteligente:

  * **Plataforma:** Easypanel.
  * **Fuente de Código:** Un repositorio Git (este mismo), usando la metodología "Push-to-Deploy".
  * **Contenedor:** Una imagen de Docker personalizada basada en `python:3.11-slim`.
  * **Proceso Principal (API):** Un servidor **Flask** se ejecuta como el proceso principal. Esto mantiene el contenedor vivo y sirve los datos a través de endpoints HTTP (ej. `/api/datos/hoy`).
  * **Proceso Secundario (Scraper):** Un servicio **Cron** se ejecuta en segundo plano *dentro del mismo contenedor*. A las 6:00 AM, ejecuta el script de Python con un argumento especial (`scrape`) para realizar la descarga de datos.
  * **Scraping:** Se usa **Selenium** con **Firefox-ESR** y un `geckodriver` de **aarch64** instalado manualmente, ya que Google Chrome no está disponible para ARM64 en Linux.
  * **Persistencia:** Se utilizan **Volúmenes** de Easypanel para que los archivos Excel (`ansv-data`) y los logs (`ansv-logs`) persistan entre reinicios y despliegues.

-----

## 📋 Requisitos Previos

  * **Servidor VPS:** Un VPS (preferentemente con arquitectura **ARM64**) con Ubuntu 20.04+ o Debian 11+.
  * **Easypanel Instalado:** Debes tener una instancia de Easypanel funcionando en tu VPS.
  * **Repositorio Git:** Este repositorio (`https://github.com/nuntius-dev/web-scraping-ansv.gov.co`) es la fuente del proyecto.

-----

## 📂 Archivos del Proyecto

Este repositorio contiene 5 archivos esenciales:

1.  **`ansv_scraper.py`**: El script de Python que contiene **tanto la lógica del scraper como la API de Flask**.
2.  **`Dockerfile`**: Las instrucciones para construir la imagen Docker, optimizada para **ARM64**, instalando Firefox-ESR y el `geckodriver` de `aarch64` manualmente.
3.  **`requirements.txt`**: Las librerías de Python necesarias (Selenium, Pandas, Flask, etc.).
4.  **`crontab`**: La definición de la tarea programada que se ejecuta a las 6:00 AM, llamando al script con el argumento `scrape`.
5.  **`entrypoint.sh`**: El script de inicio del contenedor. Inicia `cron` en segundo plano y luego `flask run` como proceso principal para servir la API.

*(Nota: No necesitas crear estos archivos, ya existen en este repositorio).*

-----

## 🚀 Guía de Despliegue en Easypanel

Esta es la guía completa para desplegar este repositorio directamente.

### Paso 1: Crear la Aplicación en Easypanel

1.  Inicia sesión en tu panel de Easypanel.
2.  Ve al proyecto deseado (ej. `clientes`).
3.  Haz clic en **"New App"** (Nueva App).

### Paso 2: Configurar la Fuente (Source)

1.  Selecciona **"Git"**.
2.  Conecta tu cuenta de GitHub (si no lo has hecho).
3.  Completa los campos **usando este repositorio**:
      * **Owner:** `nuntius-dev`
      * **Repository:** `web-scraping-ansv.gov.co`
      * **Branch:** `main` (o la rama que desees desplegar).
      * **Build Path:** `/` (déjalo como está, una sola barra).
4.  Haz clic en **"Save"** (Guardar).

### Paso 3: Configurar la Compilación (Build)

1.  Después de guardar, serás llevado a la pestaña **"Build"**.
2.  Selecciona la opción **"Dockerfile"**.
3.  En el campo "Dockerfile", escribe: `Dockerfile`
4.  Haz clic en **"Save"** (Guardar).

### Paso 4: Configurar Variables de Entorno (Environment)

1.  Ve a la pestaña **"Deploy"**.
2.  En la sección **"Environment Variables"**, añade la zona horaria:
      * **Name:** `TZ`
      * **Value:** `America/Bogota`
3.  Haz clic en **"Save"** (Guardar).

### Paso 5: Configurar Volúmenes (Storage)

¡Este paso es crítico para que tus datos persistan\!

1.  Ve a la pestaña **"Storage"** (Almacenamiento) en el menú de la izquierda de tu app.
2.  Usa **"Volume Mounts"** (Montajes de Volumen). Esto permite que Easypanel los cree y gestione por ti.
3.  **Añade el volumen de DATOS:**
      * Haz clic en **`Add Volume Mount`**.
      * **Volume Name:** `ansv-data`
      * **Container Path:** `/app/data` (Debe ser exactamente este).
4.  **Añade el volumen de LOGS:**
      * Haz clic en **`Add Volume Mount`**.
      * **Volume Name:** `ansv-logs`
      * **Container Path:** `/app/logs` (Debe ser exactamente este).

### Paso 6: Configurar Puertos (Ports)

1.  Ve a la pestaña **"Deploy"**.
2.  Baja a la sección **"Ports"**.
3.  Añade el mapeo para la API de Flask:
      * **Container Port:** `8080` (Debe ser `8080`, como se definió en `entrypoint.sh` y `Dockerfile`).
      * **Host Port:** Déjalo vacío. Easypanel asignará uno automáticamente.
4.  Haz clic en **"Save"** (Guardar).

### Paso 7: Desplegar (Deploy)

1.  Ahora, haz clic en el botón grande de **"Deploy"** (Desplegar).
2.  Easypanel clonará el repositorio, construirá la imagen de Docker (esto puede tardar varios minutos la primera vez) e iniciará el contenedor.
3.  Puedes ver el progreso en la pestaña **"Logs"**. Deberías ver la salida de Flask, indicando que el servidor está corriendo en el puerto 8080.

### Paso 8: Configurar el Dominio (Domains)

1.  Una vez que el despliegue sea exitoso y el servicio esté "Running", ve a la pestaña **"Domains"**.
2.  Añade un dominio o subdominio para acceder a tu API (ej. `ansv-api.tu-dominio.com`).
3.  Asegúrate de que apunte al puerto `8080`.
4.  Guarda y espera a que se genere el SSL.

¡Listo\! Tu API y tu scraper están 100% operativos.

-----

## 📊 Endpoints de la API (Uso)

Una vez desplegado, puedes acceder a tu API. Si tu dominio es `https://ansv-api.ejemplo.com`:

  * **Endpoint Raíz (Status):** `https://ansv-api.ejemplo.com/`

      * **Respuesta:** `{"servicio":"API de Scraper ANSV", "estado":"en_linea", ...}`
      * Útil para saber si la API está funcionando.

  * **Endpoint de Hoy:** `https://ansv-api.ejemplo.com/api/datos/hoy`

      * **Respuesta:** Devuelve un JSON con los datos de la hoja correspondiente al día de hoy (en zona horaria de Bogotá).

  * **Endpoint por Fecha:** `https://ansv-api.ejemplo.com/api/datos/fecha/YYYY-MM-DD`

      * **Ejemplo:** `.../api/datos/fecha/2025-11-14`
      * **Respuesta:** Devuelve un JSON con los datos de la hoja para la fecha especificada.

  * **Respuesta de Error (404):**

      * Si el scraper aún no se ha ejecutado o no hay datos para esa fecha, recibirás un error 404 con un mensaje JSON, ej: `{"error": "Datos para la fecha '...' no encontrados"}`.

-----

## 🔧 Mantenimiento y Pruebas en Easypanel

  * **Ver Logs de la API:**

      * Ve a la pestaña **"Logs"** de tu app. Verás la salida de Flask y los mensajes de inicio.

  * **Ver Logs del Scraper (Cron):**

      * Ve a **"Storage"** -\> (tu volumen `ansv-logs`) -\> y abre el archivo `cron.log`. Ahí verás la salida de la ejecución de las 6:00 AM.

  * **Probar el Scraper Manualmente (¡Muy útil\!):**

    1.  Ve a la pestaña **"Shell"** de tu app.
    2.  Haz clic en **"Connect"**.
    3.  En la terminal, ejecuta el comando de scrape:
        ```bash
        python /app/ansv_scraper.py scrape
        ```
    4.  Verás la salida del scraper en tiempo real. Esto es perfecto para forzar una descarga sin esperar a las 6 AM. Una vez que termine, los endpoints de la API tendrán los datos.

  * **Ver los Archivos Excel Generados:**

    1.  Ve al menú **"Storage"** en la barra lateral izquierda de Easypanel.
    2.  Busca tu volumen `ansv-data` y haz clic en él.
    3.  Podrás navegar y ver las carpetas (`2025`) y los archivos (`Noviembre.xlsx`) que ha generado el scraper.

  * **Actualizar el Código:**

    1.  Simplemente haz `git push` a tu repositorio de GitHub.
    2.  Vuelve a Easypanel y haz clic en el botón **"Deploy"**.
    3.  Easypanel detectará el nuevo commit, reconstruirá la imagen y reiniciará el servicio con el nuevo código, sin perder los datos de los volúmenes.

-----

## 🔍 Solución de Problemas (Lecciones Aprendidas)

Esta sección documenta los problemas encontrados y resueltos para que este repositorio funcione en un VPS ARM64:

  * **Problema:** `exit code: 100` y errores de dependencias `amd64`.

      * **Causa:** Se intentó instalar `google-chrome` en un servidor **ARM64 (aarch64)**. Google Chrome no tiene versión para Linux ARM64.
      * **Solución:** Se reemplazó Chrome por **`firefox-esr`**, que sí está disponible en los repositorios de Debian para ARM64.

  * **Problema:** `webdriver-manager` descarga el `geckodriver` incorrecto (`linux64` en lugar de `aarch64`).

      * **Causa:** `webdriver-manager` no detecta correctamente la arquitectura ARM64.
      * **Error Resultante:** `[Errno 8] Exec format error`.
      * **Solución:** Se eliminó `webdriver-manager`. El `Dockerfile` ahora **descarga manualmente** la versión correcta (`geckodriver-...-linux-aarch64.tar.gz`) y la coloca en `/usr/local/bin/`.

  * **Problema:** `Message: Unable to obtain driver for firefox using Selenium Manager`.

      * **Causa:** Selenium 4.6+ intenta usar su propio "Selenium Manager" si no se le especifica una ruta, y este también falla en ARM64.
      * **Solución:** Se especificó la ruta explícita en `ansv_scraper.py`: `service = Service(executable_path="/usr/local/bin/geckodriver")`.

  * **Problema:** `crontab file is missing newline before EOF`.

      * **Causa:** El sistema `cron` de Linux requiere que los archivos de crontab terminen con una línea vacía.
      * **Solución:** Se añadió `RUN echo "" >> /etc/cron.d/ansv-cron` en el `Dockerfile`.
