from sqlalchemy import Column, Integer, Float, String
from .db.connection import Base

class RegistroML(Base):
    """Modelo ORM que representa un artículo extraído desde un sitio web.

    Este modelo se corresponde con la tabla 'registros_ml' en la base de datos. 
    Almacena la información estructurada de productos obtenidos por scraping.

    Atributos:
        id (int): Identificador único del registro (clave primaria).
        nombre_articulo (str): Nombre del producto o artículo.
        precio (int): Precio del producto en COP.
        calificacion_promedio (float): Valoración promedio del producto.
        cantidad_calificaciones (int): Número de valoraciones que ha recibido.
        descripcion (str): Descripción textual del producto.
        enlace_articulo (str): URL única del artículo; actúa como campo índice único.
    """
    __tablename__ = "registros_ml"

    id = Column(Integer, primary_key=True, index=True)
    nombre_articulo = Column(String(255), nullable=False)
    precio = Column(Integer, nullable=False)
    calificacion_promedio = Column(Float)
    cantidad_calificaciones = Column(Integer)
    descripcion = Column(String)
    enlace_articulo = Column(String, unique=True, nullable=False)
