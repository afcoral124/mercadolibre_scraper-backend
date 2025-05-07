from pydantic import BaseModel, HttpUrl
from typing import Optional

class RegistroBase(BaseModel):
    """Esquema base que define los campos comunes de un artículo.

    Utilizado para validar la entrada y salida de datos en la API.

    Atributos:
        nombre_articulo (str): Nombre del producto o artículo.
        precio (int): Precio del producto en COP.
        calificacion_promedio (Optional[float]): Valoración promedio del producto (puede no estar disponible).
        cantidad_calificaciones (Optional[int]): Número de personas que calificaron el producto.
        descripcion (Optional[str]): Descripción textual del producto.
        enlace_articulo (HttpUrl): URL del artículo en el sitio web de origen.
    """
    nombre_articulo: str
    precio: int
    calificacion_promedio: Optional[float] = None
    cantidad_calificaciones: Optional[int] = None
    descripcion: Optional[str] = None
    enlace_articulo: HttpUrl


class RegistroCreate(RegistroBase):
    """Esquema utilizado para validar los datos al crear un nuevo registro.

    Hereda todos los campos de RegistroBase.
    """
    pass


class Registro(RegistroBase):
    """Esquema de respuesta que incluye el ID del registro almacenado.

    Utilizado al devolver datos al cliente. Incluye configuración para trabajar con ORM.

    Atributos:
        id (int): Identificador único del registro en la base de datos.
    """
    id: int

    class Config:
        orm_mode = True
