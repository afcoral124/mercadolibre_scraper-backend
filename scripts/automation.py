import argparse
import requests
import asyncio
import os
import pandas as pd
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.scraper import (
    obtener_url_todos_los_articulos,
    scrapear_lista_articulos_async,
    limpiar_datos_articulos
)

# Configuración
API_URL = "http://localhost:8000/registros/"
LOG_FILE = "logs/automation_log.txt"


# Crear carpetas si no existen
os.makedirs("logs", exist_ok=True)
os.makedirs("backups", exist_ok=True)


def log_mensaje(mensaje):
    """Escribe un mensaje en el archivo de log con marca de tiempo.

    Args:
        mensaje (str): Mensaje a registrar en el archivo de log (varía según donde se llama a esta función).

    """
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {mensaje}\n")

def obtener_enlaces_existentes():
    """
    Recupera todos los enlaces de artículos ya registrados en la base de datos a través de la API REST.

    Utiliza paginación con los parámetros `skip` y `limit` para solicitar todos los registros de la API
    en bloques sucesivos. Normaliza los enlaces para facilitar la comparación con nuevos registros:
    - Elimina parámetros (`#` y después).
    - Elimina `/` al final.
    - Convierte a minúsculas.

    Returns:
        set: Conjunto de enlaces normalizados (str) correspondientes a artículos ya almacenados en la base de datos.
    """
    enlaces = set()
    skip = 0
    limit = 1000

    while True:
        try:
            response = requests.get(API_URL, params={"skip": skip, "limit": limit})
            if response.status_code != 200:
                print(f"Error al obtener registros existentes: {response.status_code}")
                break

            registros = response.json()
            if not registros:
                break

            enlaces.update(r["enlace_articulo"].split("#")[0].strip().rstrip("/").lower() for r in registros)
            skip += limit

        except Exception as e:
            print(f"Excepción al obtener registros existentes: {e}")
            break

    return enlaces

def enviar_registro(registro, resumen):
    """
    Envía un registro individual a la API REST y actualiza el resumen del proceso según el resultado.

    Realiza una petición HTTP POST al endpoint configurado, maneja errores HTTP comunes
    y captura excepciones generales. También registra en logs en caso de error o excepción.

    Args:
        registro (dict): Diccionario con los datos del artículo a enviar. 
            Debe contener al menos 'nombre_articulo' y 'enlace_articulo'.
        resumen (dict): Diccionario con contadores del proceso, con claves:
            - 'enviados' (int)
            - 'duplicados' (int)
            - 'errores' (int)

    Returns:
        None
    """
    try:
        response = requests.post(API_URL, json=registro)
        if response.status_code == 201:
            print(f"Enviado: {registro['nombre_articulo']}")
            resumen["enviados"] += 1
        elif response.status_code == 409:
            print(f"Duplicado: {registro['nombre_articulo']}")
            resumen["duplicados"] += 1
        else:
            print(f"Error HTTP {response.status_code}: {registro['nombre_articulo']}")
            resumen["errores"] += 1
            log_mensaje(f"Error HTTP {response.status_code} - {registro['enlace_articulo']}")
    except Exception as e:
        print(f"Excepción al enviar {registro['nombre_articulo']}: {e}")
        resumen["errores"] += 1
        log_mensaje(f"Excepción: {e} - {registro['enlace_articulo']}")


def imprimir_saludo():
    """Imprime un saludo inicial y la fecha actual en la consola, además una imagen muy feliz y amigable :)

    Este saludo incluye el nombre del script y la fecha actual, formateada como 'dd/mm/yyyy'.

    Returns:
        None
    """
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    print(f"Hola! :), este es el script de automatización de scraping y carga en API REST. Fecha: {fecha_actual}")
    saludo = r"""
    ´´´´´´´´´´´´´´´´´´´´´´¶¶¶¶¶¶¶¶¶
    ´´´´´´´´´´´´´´´´´´´´¶¶´´´´´´´´´´¶¶
    ´´´´´´¶¶¶¶¶´´´´´´´¶¶´´´´´´´´´´´´´´¶¶
    ´´´´´¶´´´´´¶´´´´¶¶´´´´´¶¶´´´´¶¶´´´´´¶¶
    ´´´´´¶´´´´´¶´´´¶¶´´´´´´¶¶´´´´¶¶´´´´´´´¶¶
    ´´´´´¶´´´´¶´´¶¶´´´´´´´´¶¶´´´´¶¶´´´´´´´´¶¶
    ´´´´´´¶´´´¶´´´¶´´´´´´´´´´´´´´´´´´´´´´´´´¶¶
    ´´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´´´´´´´´´´´´´´´´´´´´¶¶
    ´´´¶´´´´´´´´´´´´¶´¶¶´´´´´´´´´´´´´¶¶´´´´´¶¶
    ´´¶¶´´´´´´´´´´´´¶´´¶¶´´´´´´´´´´´´¶¶´´´´´¶¶
    ´¶¶´´´¶¶¶¶¶¶¶¶¶¶¶´´´´¶¶´´´´´´´´¶¶´´´´´´´¶¶
    ´¶´´´´´´´´´´´´´´´¶´´´´´¶¶¶¶¶¶¶´´´´´´´´´¶¶
    ´¶¶´´´´´´´´´´´´´´¶´´´´´´´´´´´´´´´´´´´´¶¶
    ´´¶´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´´´´´´´´´´´´´´´¶¶
    ´´¶¶´´´´´´´´´´´¶´´¶¶´´´´´´´´´´´´´´´´¶¶
    ´´´¶¶¶¶¶¶¶¶¶¶¶¶´´´´´¶¶´´´´´´´´´´´´¶¶
    ´´´´´´´´´´´´´´´´´´´´´´´¶¶¶¶¶¶¶¶¶¶¶
    """
    print(saludo)
    print("\n{:^80}\n".format("Bienvenido al sistema de scraping de Mercado Libre"))


async def main(args):
    """
    Ejecuta el flujo completo de automatización: scraping, limpieza, backup y carga en API REST.

    Pasos:
    1. Obtiene las URLs de artículos desde Mercado Libre en función del término y cantidad de páginas.
    2. Realiza scraping asincrónico de cada URL con concurrencia controlada.
    3. Limpia y estructura los datos obtenidos.
    4. (Opcional) Guarda los datos limpios en un archivo CSV con timestamp.
    5. Consulta los enlaces ya registrados en la base de datos para evitar duplicados.
    6. Envía los nuevos registros a la API.
    7. Imprime y registra un resumen final del proceso.

    Args:
        args (argparse.Namespace): Argumentos parseados desde la CLI, que incluyen:
            - articulo (str): Término de búsqueda.
            - paginas (int): Número máximo de páginas a scrapear.
            - concurrencia (int): Límite de peticiones simultáneas.
            - guardar_csv (bool): Si se activa, guarda un CSV de respaldo.

    Returns:
        None
    """
    resumen = {"enviados": 0, "duplicados": 0, "errores": 0}

    imprimir_saludo()

    log_mensaje(f"Inicio de proceso: artículo='{args.articulo}', páginas={args.paginas}")

    print(f"\nBuscando '{args.articulo}' en Mercado Libre...")
    urls = obtener_url_todos_los_articulos(args.articulo, args.paginas)
    print(f"{len(urls)} enlaces encontrados.")

    datos_scrapeados = await scrapear_lista_articulos_async(urls, args.concurrencia)
    print(f"{len(datos_scrapeados)} artículos scrapeados.")

    datos_limpios = limpiar_datos_articulos(datos_scrapeados)
    print(f"{len(datos_limpios)} artículos limpiados.")

    if args.guardar_csv:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backups/dataset_{args.articulo.replace(' ', '_')}_{timestamp}.csv"
        pd.DataFrame(datos_limpios).to_csv(filename, index=False)
        print(f"CSV guardado en: {filename}")
        log_mensaje(f"CSV guardado: {filename}")

    # Obtener enlaces existentes desde la API antes de enviar
    enlaces_existentes = obtener_enlaces_existentes()
    print(f"{len(enlaces_existentes)} enlaces ya registrados en la base de datos.")

    print(f"Enviando artículos a la API...")
    for registro in datos_limpios:
        if registro["enlace_articulo"] in enlaces_existentes:
            print(f"Duplicado (omitido antes de enviar): {registro['nombre_articulo']}")
            resumen["duplicados"] += 1
            continue
        enviar_registro(registro, resumen)

    print("\nAutomatización completada.")
    print(f"{resumen['enviados']} enviados | {resumen['duplicados']} duplicados | {resumen['errores']} errores")
    log_mensaje(f"Resumen: {resumen['enviados']} enviados, {resumen['duplicados']} duplicados, {resumen['errores']} errores.\n")



if __name__ == "__main__":
    # ===============================================
    # Punto de entrada del script de automatización
    # ===============================================
    # Este bloque configura la interfaz de línea de comandos (CLI)
    # usando argparse, para controlar el scraping y la carga de datos.
    #
    # Argumentos:
    # --articulo       (str): Término de búsqueda.
    # --paginas        (int): Número máximo de páginas a scrapear (default=3).
    # --concurrencia   (int): Número de peticiones simultáneas (default=10).
    # --guardar_csv    (flag): Si se activa, guarda los resultados en un archivo CSV.
    #
    # Ejecuta la función principal 'main(args)' en un entorno asincrónico.
    parser = argparse.ArgumentParser(description="Automatización de scraping y carga en API REST con backups y logs.")

    parser.add_argument("--articulo", required=True, help="Artículo a buscar")
    parser.add_argument("--paginas", type=int, default=3, help="Cantidad de páginas a scrapear")
    parser.add_argument("--concurrencia", type=int, default=10, help="Número de peticiones simultáneas (concurrency limit)")
    parser.add_argument("--guardar_csv", action="store_true", help="Guardar resultados en CSV")

    args = parser.parse_args()
    asyncio.run(main(args))