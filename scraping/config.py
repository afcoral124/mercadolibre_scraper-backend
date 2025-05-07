# ARCHIVO CON LAS VARIABLES DE CONFIGURACIÓN DEL SCRAPER
ARTICULO = "laptop" # Artículo a buscar
MAX_PAGINAS = 1 # Número máximo de páginas a scrapear
CONCURRENCY_LIMIT = 100 # Límite de concurrencia para las solicitudes con el Semaphore (controla cuan "agresivo" y rápido es el scraper)

# cabecera de la solicitud
# User-Agent y otros encabezados para simular un navegador web
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.google.com"
}