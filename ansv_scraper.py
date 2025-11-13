#!/usr/bin/env python3
"""
Script de PRODUCCIÓN para descargar archivo Excel de ubicaciones ANSV
Se ejecuta diariamente a las 6 AM mediante cron
Requiere: selenium, webdriver-manager, openpyxl, pandas
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook
import shutil
import logging
import sys

# Configurar logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"ansv_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

def descargar_excel_temporal(url, carpeta_temp="temp_descargas"):
    """
    Descarga el archivo Excel a una carpeta temporal
    """
    carpeta_completa = os.path.abspath(carpeta_temp)
    
    # Limpiar carpeta temporal si existe
    if os.path.exists(carpeta_completa):
        shutil.rmtree(carpeta_completa)
    os.makedirs(carpeta_completa)
    
    chrome_options = Options()
    prefs = {
        "download.default_directory": carpeta_completa,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")  # Modo sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logging.info("Accediendo a la página de ANSV...")
        driver.get(url)
        time.sleep(3)
        
        # Buscar y cambiar al iframe
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        logging.info("Iframe encontrado, cambiando contexto...")
        time.sleep(2)
        
        # Buscar el botón de descarga
        selectores_posibles = [
            "//div[contains(@class, 'dx-datagrid-export-button')]",
            "//div[@aria-label='export-excel-button']",
            "//div[@title='Exportar todo']",
        ]
        
        boton = None
        for selector in selectores_posibles:
            try:
                boton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except:
                continue
        
        if not boton:
            logging.error("No se encontró el botón de descarga")
            driver.quit()
            return None
        
        logging.info("Botón de descarga encontrado, haciendo clic...")
        try:
            boton.click()
        except:
            driver.execute_script("arguments[0].click();", boton)
        
        # Esperar a que se complete la descarga
        tiempo_espera = 60
        tiempo_transcurrido = 0
        
        while tiempo_transcurrido < tiempo_espera:
            archivos = os.listdir(carpeta_completa)
            archivos_excel = [f for f in archivos if f.endswith(('.xlsx', '.xls')) and not f.endswith('.crdownload')]
            
            if archivos_excel:
                archivo_descargado = os.path.join(carpeta_completa, archivos_excel[0])
                logging.info(f"Archivo descargado exitosamente: {archivos_excel[0]}")
                driver.quit()
                return archivo_descargado
            
            time.sleep(1)
            tiempo_transcurrido += 1
        
        logging.error("Tiempo de espera agotado para la descarga")
        driver.quit()
        return None
        
    except Exception as e:
        logging.error(f"Error durante la descarga: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def extraer_fecha_del_nombre(nombre_archivo):
    """
    Extrae la fecha del nombre del archivo descargado
    Formato esperado: 202510032325-ansv-fotodeteccion.xlsx
    Retorna: "2025-10-03" o None si no se puede extraer
    """
    try:
        nombre_base = os.path.basename(nombre_archivo)
        fecha_parte = nombre_base.split('-')[0]
        
        if len(fecha_parte) >= 8:
            año = fecha_parte[0:4]
            mes = fecha_parte[4:6]
            dia = fecha_parte[6:8]
            
            fecha_formateada = f"{año}-{mes}-{dia}"
            logging.info(f"Fecha extraída del archivo: {fecha_formateada}")
            return fecha_formateada
        else:
            return None
    except Exception as e:
        logging.warning(f"No se pudo extraer fecha del nombre: {str(e)}")
        return None

def obtener_nombre_mes(numero_mes):
    """
    Convierte número de mes a nombre en español
    """
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    return meses.get(numero_mes, "Desconocido")

def agregar_hoja_a_excel(archivo_origen, archivo_destino, nombre_hoja):
    """
    Agrega el contenido del archivo_origen como una nueva hoja en archivo_destino
    """
    try:
        df = pd.read_excel(archivo_origen)
        
        if not os.path.exists(archivo_destino):
            logging.info(f"Creando nuevo archivo: {os.path.basename(archivo_destino)}")
            df.to_excel(archivo_destino, sheet_name=nombre_hoja, index=False)
        else:
            logging.info(f"Agregando hoja '{nombre_hoja}' al archivo existente")
            with pd.ExcelWriter(archivo_destino, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=nombre_hoja, index=False)
        
        return True
    except Exception as e:
        logging.error(f"Error al agregar hoja: {str(e)}")
        return False

def ejecutar_descarga_diaria():
    """
    Ejecuta la descarga diaria del archivo Excel de ANSV
    """
    url = "https://fotodeteccion.ansv.gov.co/ubicaciones-aprobadas.html"
    
    # Obtener fecha actual
    ahora = datetime.now()
    año_actual = ahora.year
    mes_actual = ahora.month
    dia_actual = ahora.day
    
    # Crear estructura de carpetas
    carpeta_año = str(año_actual)
    if not os.path.exists(carpeta_año):
        os.makedirs(carpeta_año)
        logging.info(f"Carpeta '{carpeta_año}' creada")
    
    # Nombre del archivo del mes
    nombre_mes = obtener_nombre_mes(mes_actual)
    archivo_mes = os.path.join(carpeta_año, f"{nombre_mes}.xlsx")
    
    logging.info("=" * 70)
    logging.info("INICIO DE DESCARGA DIARIA - ANSV FOTODETECCIÓN")
    logging.info("=" * 70)
    logging.info(f"Fecha: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Archivo destino: {archivo_mes}")
    
    # Descargar archivo temporal
    logging.info("Iniciando descarga desde ANSV...")
    archivo_temporal = descargar_excel_temporal(url)
    
    if archivo_temporal:
        # Extraer fecha del nombre del archivo
        fecha_extraida = extraer_fecha_del_nombre(archivo_temporal)
        
        if fecha_extraida:
            nombre_hoja = fecha_extraida
        else:
            # Fallback: usar fecha actual
            nombre_hoja = f"{año_actual}-{mes_actual:02d}-{dia_actual:02d}"
            logging.warning(f"Usando fecha actual como fallback: {nombre_hoja}")
        
        # Agregar al archivo del mes
        logging.info("Procesando y agregando hoja al archivo mensual...")
        if agregar_hoja_a_excel(archivo_temporal, archivo_mes, nombre_hoja):
            logging.info(f"✓ Hoja '{nombre_hoja}' agregada exitosamente")
            
            # Mostrar información del archivo
            try:
                wb = load_workbook(archivo_mes)
                logging.info(f"El archivo ahora tiene {len(wb.sheetnames)} hoja(s)")
                logging.info(f"Hojas: {', '.join(wb.sheetnames)}")
                wb.close()
            except:
                pass
            
            logging.info("=" * 70)
            logging.info("✓ DESCARGA COMPLETADA EXITOSAMENTE")
            logging.info("=" * 70)
            
            # Limpiar carpeta temporal
            if os.path.exists("temp_descargas"):
                shutil.rmtree("temp_descargas")
            
            return True
        else:
            logging.error("Error al agregar la hoja al archivo")
            return False
    else:
        logging.error("No se pudo descargar el archivo")
        logging.info("=" * 70)
        logging.info("✗ DESCARGA FALLIDA")
        logging.info("=" * 70)
        return False

if __name__ == "__main__":
    try:
        resultado = ejecutar_descarga_diaria()
        sys.exit(0 if resultado else 1)
    except Exception as e:
        logging.error(f"Error crítico: {str(e)}")
        sys.exit(1)
