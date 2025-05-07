from fastapi import FastAPI
from .routers import registros_ml

app = FastAPI(
    title="API MercadoLibre Scraper",
    description="REST API para consultar registros de productos extraídos de MercadoLibre.",
    version="1.0.0"
)

app.include_router(registros_ml.router)
