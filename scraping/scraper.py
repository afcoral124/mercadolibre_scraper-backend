import requests
import asyncio
import aiohttp
import pandas as pd
import random
import time
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.robotparser import RobotFileParser
sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraping.config import ARTICULO, MAX_PAGINAS, CONCURRENCY_LIMIT, HEADERS




#Leer el archivo robots.txt para asegurarse de que la URL es accesible
rp = RobotFileParser()
rp.set_url("https://www.mercadolibre.com/robots.txt")
rp.read()

def obtener_url_articulos(base_url):
    """
    Extrae los enlaces de los artículos listados en una página de resultados de búsqueda de Mercado Libre.

    Args:
        base_url (str): URL de la página de resultados a procesar.

    Returns:
        tuple:
            bool: Indica si se encontraron artículos en la página (True) o no (False).
            list: Lista de URLs (str) correspondientes a cada artículo encontrado en la página.
    """
    try:
        res = requests.get(base_url, headers=HEADERS, timeout=10)
        res.raise_for_status()  # Lanza una excepción si la respuesta fue un error HTTP
    except requests.RequestException as e:
        print(f"Error al hacer la solicitud HTTP durante la obtención de los url de los artículos en la página {base_url}  | Error: {e}")
        return False, []

    soup = BeautifulSoup(res.text, "html.parser")
    lista_url_articulos = []

    # Buscar los contenedores de artículos
    articulos = soup.find_all("div", class_="poly-card")

    if not articulos:
        return False, []

    for item in articulos:
        enlace = item.find("a", class_="poly-component__title")
        if enlace and enlace.get("href"):
            lista_url_articulos.append(enlace["href"])
    
    return True, lista_url_articulos



def obtener_url_todos_los_articulos(articulo, max_paginas):
    """
    Recorre múltiples páginas de resultados de Mercado Libre para obtener enlaces de artículos relacionados con una búsqueda.

    Construye dinámicamente las URLs de paginación a partir del nombre del artículo, 
    invoca `obtener_url_articulos` en cada página y continúa hasta que no haya más resultados
    o se alcance el número máximo de páginas especificado.

    Args:
        articulo (str): Nombre o palabra clave del artículo a buscar (por ejemplo, "audifonos inalambricos").
        max_paginas (int): Número máximo de páginas a recorrer como límite de seguridad.

    Returns:
        list: Lista con los enlaces de todos los artículos encontrados en todas las páginas recorridas.
    """
    lista_total_url_articulos = []
    pagina = 0
    seguir = True
    
    while seguir and pagina < max_paginas:
        
        offset = pagina * 50 + 1
        url = "https://listado.mercadolibre.com.co/{}_Desde_{}_NoIndex_True".format(articulo.replace(" ", "-"), offset)

        #Verificar si la URL es accesible según el archivo robots.txt
        if rp.can_fetch(HEADERS["User-Agent"], url):
            print("Permitido según robots.txt")
        else:
            print("Prohibido según robots.txt")
            
        print(f"\n Procesando pagina {pagina + 1} de {max_paginas}")
        flag, urls = obtener_url_articulos(url)
        
        

        if not flag or not urls:
            print(" No se encontraron mas resultados. Deteniendo...")
            seguir = False
        else:
            lista_total_url_articulos.extend(urls)
            pagina += 1

    return lista_total_url_articulos



async def fetch_html(session, url):
    """
    Realiza una petición HTTP asíncrona para obtener el contenido HTML de una página web.

    Args:
        session (aiohttp.ClientSession): Sesión HTTP asíncrona reutilizable para optimizar las conexiones.
        url (str): URL de la página web a la que se desea acceder.

    Returns:
        str or None: Contenido HTML de la respuesta si la solicitud es exitosa, o None en caso de error de red o HTTP.
    """
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        #print(f"Error al hacer request de la pagina de un arrticulo cuyo enlace es {url} | Detalles del error: {e}")
        return None

async def parse_articulo(html, url):
    """
    Extrae información estructurada de un artículo a partir de su HTML.

    Analiza el contenido HTML y extrae los siguientes datos:
        - Nombre del artículo.
        - Precio.
        - Calificación promedio del producto (si está disponible).
        - Cantidad total de calificaciones.
        - Descripción compuesta por las características destacadas.
        - Enlace del artículo (URL original proporcionada).

    Args:
        html (str): Código HTML de la página del artículo.
        url (str): URL del artículo, incluida en los datos finales por trazabilidad.

    Returns:
        dict or None: Diccionario con los datos del artículo, incluyendo nombre, precio, calificación, descripción, etc.
                      Retorna None si ocurre un error al parsear el HTML.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        nombre_articulo = soup.find("h1", {"class": "ui-pdp-title"}).text
        precio = soup.find("span", {"class": "andes-money-amount__fraction"}).text
        calificacion_promedio = soup.find("span", {"class": "ui-pdp-review__rating"}).text
        cantidad_calificaciones = soup.find("span", {"class": "ui-pdp-review__amount"}).text
        caracteristicas = soup.find_all("li", class_="ui-vpp-highlighted-specs__features-list-item")
        descripcion = " | ".join(c.text.strip() for c in caracteristicas)

        return {
            "nombre_articulo": nombre_articulo,
            "precio": precio,
            "calificacion_promedio": calificacion_promedio,
            "cantidad_calificaciones": cantidad_calificaciones,
            "descripcion": descripcion,
            "enlace_articulo": url
        }
    except Exception as e:
        #print(f"El artículo no tiene todos los atributos buscados. Error al parsear HTML de {url} | Detalles del error: {e}")
        return None

async def procesar_url(session, url, semaphore):
    """
    Orquesta la descarga y procesamiento de un artículo específico, respetando un límite de concurrencia.

    Esta función coordina la obtención del HTML de un artículo y su posterior análisis, utilizando un semáforo
    asíncrono (semaphore) para garantizar que no se exceda el número máximo permitido de solicitudes HTTP simultáneas.
    El uso del semáforo previene sobrecargar el servidor y reduce el riesgo de bloqueos por parte del sitio web.

    Args:
        session (aiohttp.ClientSession): Sesión HTTP asíncrona para realizar las peticiones HTTP.
        url (str): URL del artículo a scrapear.
        semaphore (asyncio.Semaphore): Semáforo asíncrono que limita la cantidad de solicitudes concurrentes activas.

    Returns:
        dict or None: Diccionario con los datos estructurados del artículo si la descarga y parsing son exitosos;
                      None si falla la obtención del HTML o el análisis del contenido.
    """
    #Semáforo para configurar concurrencia de peticiones HTTP y evitar sobrecargar el servidor y posteriores bloqueos a la IP
    
    async with semaphore:
        html = await fetch_html(session, url)
        if html:
            return await parse_articulo(html, url)
        # Si no se pudo obtener el HTML, se retorna None
        return None

async def scrapear_lista_articulos_async(urls, limite_concurrencia):
    """
    Gestiona el scraping asíncrono de múltiples artículos en paralelo, respetando un límite de concurrencia.

    Esta función crea un semáforo asíncrono (asyncio.Semaphore) para limitar la cantidad de solicitudes
    HTTP concurrentes activas, inicializa una sesión HTTP asíncrona y coordina la ejecución paralela
    de las tareas de scraping mediante asyncio.gather(). Al finalizar, filtra los resultados exitosos.

    Args:
        urls (list of str): Lista de URLs de artículos a scrapear.
        limite_concurrencia (int): Número máximo de solicitudes HTTP concurrentes permitidas.

    Returns:
        list of dict: Lista de diccionarios con los datos de cada artículo scrapeado exitosamente.
    """
    semaphore = asyncio.Semaphore(limite_concurrencia)
    async with aiohttp.ClientSession() as session:
        tareas = [procesar_url(session, url, semaphore) for url in urls]
        resultados = await asyncio.gather(*tareas)

    # Filtrar los resultados exitosos
    return [r for r in resultados if r is not None]


def limpiar_datos_articulos(lista_articulos):
    """
    Limpia y normaliza una lista de diccionarios con datos de artículos scrapeados.

    Esta función:
    - Filtra artículos incompletos o con errores.
    - Convierte valores a sus tipos adecuados (int, float, str).
    - Elimina caracteres innecesarios y normaliza URLs.
    - Ignora artículos con errores de tipo o conversión.

    Args:
        lista_articulos (list): Lista de diccionarios que representan artículos
            con campos potencialmente inconsistentes o sin limpiar.

    Returns:
        list: Lista de diccionarios limpios y válidos con la siguiente estructura:
            - nombre_articulo (str)
            - precio (int)
            - calificacion_promedio (float)
            - cantidad_calificaciones (int)
            - descripcion (str)
            - enlace_articulo (str) [normalizado, sin parámetros ni #]
    """

    datos_limpios = []

    for articulo in lista_articulos:
        if not articulo:
            continue  # Ignora elementos None
        
        try:
            # Convertir y limpiar datos usando get() para evitar KeyError
            nombre = articulo.get("nombre_articulo", "").strip()
            enlace = articulo.get("enlace_articulo", "").split("#")[0].strip().rstrip("/").lower()
            precio = int(str(articulo.get("precio", 0)).strip().replace(".", ""))
            calificacion = float(str(articulo.get("calificacion_promedio", 0.0)).strip().replace(",", "."))
            cantidad_calificaciones = int(str(articulo.get("cantidad_calificaciones", 0)).strip().replace("(", "").replace(")", ""))
            descripcion = articulo.get("descripcion", "").strip()

            if nombre and enlace:
                datos_limpios.append({
                    "nombre_articulo": nombre,
                    "precio": precio,
                    "calificacion_promedio": calificacion,
                    "cantidad_calificaciones": cantidad_calificaciones,
                    "descripcion": descripcion,
                    "enlace_articulo": enlace
                })
                
        except (ValueError, TypeError) as e:
            #Si un artículo no tiene el formato esperado, se ignora y no se añade a la lista
            continue

    return datos_limpios


def guardar_en_csv(lista_diccionarios, articulo):
    """
    Guarda una lista de diccionarios en un archivo CSV con nombre dinámico basado en la fecha y hora actual.

    El nombre del archivo se genera con el formato:
        dataset_{articulo}_{YYYY-MM-DD_HH-MM-SS}.csv

    Args:
        lista_diccionarios (list[dict]): Lista de artículos con los campos a guardar.
        articulo (str): Término de búsqueda, usado como prefijo en el nombre del archivo.

    Returns:
        str or None: Ruta del archivo CSV generado, o None si no se guardó nada.
    """
    if not lista_diccionarios:
        print("La lista de datos está vacía. No se creó el archivo CSV.")
        return None

    try:
        # Generar timestamp en formato seguro para nombres de archivo
        prefijo_nombre=articulo.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"dataset_{prefijo_nombre}_{timestamp}.csv"

        df = pd.DataFrame(lista_diccionarios)
        df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        print(f"Archivo CSV con {len(lista_diccionarios)} articulos ha sido guardado exitosamente: {nombre_archivo}")
        return nombre_archivo
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo CSV: {e}")
        return None
    
    
async def main():
    """
    Función principal que orquesta el proceso completo de scraping, limpieza y almacenamiento de datos.

    Flujo de ejecución:
    1. Obtiene todas las URLs de productos desde Mercado Libre, realizando paginación.
    2. Realiza scraping asincrónico sobre cada URL encontrada.
    3. Limpia y estructura los datos extraídos.
    4. Guarda los datos limpios en un archivo CSV con nombre dinámico basado en la fecha/hora actual.

    Variables utilizadas (importadas desde config):
        - ARTICULO (str): Término de búsqueda.
        - MAX_PAGINAS (int): Cantidad máxima de páginas a recorrer.
        - CONCURRENCY_LIMIT (int): Límite de peticiones concurrentes.

    Nota:
        Esta función no retorna nada. Ejecuta acciones con efectos secundarios (impresiones y escritura de archivos).
        Debe ser llamada dentro de un entorno asincrónico usando `asyncio.run(main())`.
    """
    lista_urls = obtener_url_todos_los_articulos(ARTICULO, MAX_PAGINAS)
    datos_scrapeados = await scrapear_lista_articulos_async(lista_urls, CONCURRENCY_LIMIT)
    datos_limpios = limpiar_datos_articulos(datos_scrapeados)
    guardar_en_csv(datos_limpios, "mercado_libre")
#

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(main())

