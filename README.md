# Proyecto: Automatización de Scraping y Backend para Mercado Libre

Este proyecto implementa un sistema completo de scraping, procesamiento y almacenamiento de información sobre productos en venta en [mercadolibre.com.co](https://www.mercadolibre.com.co/). El sistema incluye:

* Scraper asincrónico con limpieza de datos.
* API REST en FastAPI conectada a una base de datos PostgreSQL en la nube.
* Script de automatización con respaldo y carga incremental.

Se scrapean los siguientes campos de los artículos:

* nombre_articulo (str): Nombre del producto o artículo.
* precio (int): Precio del producto en COP.
* calificacion_promedio (float): Valoración promedio del producto.
* antidad_calificaciones (int): Número de valoraciones que ha recibido.
* descripcion (str): Descripción textual del producto.
* enlace_articulo (str): URL única del artículo.

Con estos campos extraidos puede realizarse un posterior análisis de mercado, entender cuales son los precios más competitivos, analizar qué productos representan un mejor beneficio en términos de calidad/precio contrastando las variables de calificaciones con la del precio, monitoreo de catálogos, etc.


---

## 🤝 Stack Tecnológico y Justificación

| Tecnología              | Rol                       | Justificación                                                                |
| ----------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| **Python 3.10+**        | Lenguaje principal        | Sencillo, robusto y con librerías maduras.                                   |
| **FastAPI**             | Backend REST API          | Rápido, moderno y con validación automática (Pydantic).                      |
| **PostgreSQL (Render)** | Base de datos en la nube  | Robusta, gratuita en Render, soporte JSON.                                   |
| **SQLAlchemy**          | ORM                       | Permite manejar la base de datos como objetos, con flexibilidad y seguridad. |
| **requests / aiohttp**  | HTTP sync/async           | Para scraping y concurrencia.                                                |
| **BeautifulSoup**       | Parser HTML               | Limpieza de contenido web.                                                   |
| **pandas**              | Manejo de datos tabulares | Escritura de CSVs y depuración.                                              |
| **argparse**            | CLI                       | Parametrización del script.                                                  |

---

## 🚀 Estructura del Proyecto

```bash
mercadolibre_scraper_backend/
├── backend/
│   ├── app/
│   │   ├── db/           # Conexión y esquema de base de datos
│   │   ├── routers/      # Endpoints FastAPI
│   │   └── main.py      # Inicialización del servidor
├── scraping/              # Lógica del scraper
├── scripts/
│   └── automation.py   # Script CLI para ejecutar todo el flujo
├── backups/               # CSVs generados por scraping
├── logs/                  # Registros de ejecución
├── .env                   # Variables de entorno sensibles
├── requirements.txt       # Dependencias del proyecto
└── README.md
```

---

## 🔎 Flujo General del Proyecto

1. **Scraper** busca productos según un término de búsqueda y hace scraping asincrónico.
2. **Limpieza de datos** normaliza precios, enlaces, descripciones y calificaciones.
3. **Verificación incremental**: se consultan los enlaces ya almacenados en la base de datos para evitar duplicados.
4. **Carga a la API REST**: los registros nuevos se envían al backend en FastAPI.
5. **Backup**: se guarda un CSV local con los resultados scrapeados.
6. **Logs**: se registran errores, resumen del proceso y timestamp.

---

## 🏗️ Diagrama de Arquitectura

```
           +----------------------+     +------------------+
           |   Script CLI (user)  | --> | automation.py     |
           +----------------------+     +--------+---------+
                                                 |
                                                 |
                                         +-------v--------+
                                         | scraping/      |
                                         | scraper.py     |
                                         +-------+--------+
                                                 |
                                       +---------v----------+
                                       | BeautifulSoup +    |
                                       | Aiohttp/Requests   |
                                       +---------+----------+
                                                 |
                                         +-------v--------+
                                         | Limpieza CSV    |
                                         +-------+--------+
                                                 |
                                  +--------------v-------------+
                                  |  FastAPI Backend            |
                                  |  Routers + Schemas         |
                                  +--------------+-------------+
                                                 |
                                  +--------------v-------------+
                                  |   SQLAlchemy ORM Models     |
                                  +--------------+-------------+
                                                 |
                                         +-------v--------+
                                         | PostgreSQL DB  |
                                         | Render Cloud   |
                                         +----------------+
```

---

## 📃 Tabla de Funciones Clave

| Archivo         | Función                           | Propósito                                                     |
| --------------- | --------------------------------- | ------------------------------------------------------------- |
| `scraper.py`    | `obtener_url_todos_los_articulos` | Paginación de resultados y recolección de URLs de productos.  |
|                 | `scrapear_lista_articulos_async`  | Scraping asincrónico de cada producto.                        |
|                 | `limpiar_datos_articulos`         | Normalización de precios, enlaces, y validación de registros. |
|                 | `guardar_en_csv`                  | Almacenamiento local con timestamp.                           |
| `automation.py` | `main(args)`                      | Orquesta scraping + limpieza + backup + carga.                |
|                 | `obtener_enlaces_existentes`      | Recupera enlaces desde la API con paginación.                 |
|                 | `enviar_registro`                 | POST a la API con manejo de errores y duplicados.             |

---

## ⚖️ Despliegue y Ejecución

### 1. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate   # (Windows)
pip install -r requirements.txt
```

### 2. Configurar las variables en `.env`

```env
DB_HOST=your-db-host.render.com
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=your-db-port
```

### 3. Iniciar la API (desde la carpeta `backend`)

```bash
uvicorn app.main:app --reload
```

### 4. Ejecutar el scraper con CLI o cron

Con CLI:
```bash
python scripts/automation.py --articulo "laptop hp" --paginas 3 --guardar_csv --concurrencia 50
```

Con Cron (Por ejemplo para ejecutar todos los días a las 09:00 AM):
```bash
crontab -e

0 9 * * * /usr/bin/python3 /ruta/completa/al/proyecto/scripts/automation.py --articulo "laptop hp" --paginas 3 --guardar_csv --concurrencia 50 >> /ruta/completa/al/proyecto/logs/cron.log 2>&1
```

---

## 🎥 Video de Demostración

Video del Scraper en ejecución:
https://youtu.be/u4GSGzfMa2g?si=OV6IExebIwkjr5jG

Video del Script de automatización + API Rest & Endpoints + Base de datos desplegada en la nube
https://youtu.be/ZLPAyebJn34?si=BdysK0i7pAR1ByQ5

---

## 🔖 Recomendaciones Finales

* El sistema está preparado para correr diariamente como tarea programada (cron).
* Se pueden ampliar los campos de scraping según la categoría del producto.
* Ideal para monitorear precios, disponibilidad o cambios en catálogos.

---


