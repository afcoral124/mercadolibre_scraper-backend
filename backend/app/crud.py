from sqlalchemy.orm import Session
from . import models, schemas

def crear_registro(db: Session, registro: schemas.RegistroCreate):
    """Crea un nuevo registro en la base de datos.

    Args:
        db (Session): Sesión de SQLAlchemy para interactuar con la base de datos.
        registro (schemas.RegistroCreate): Objeto con los datos del nuevo registro a crear.

    Returns:
        models.RegistroML: El registro creado con sus datos completos, incluyendo ID generado.
    """
    db_registro = models.RegistroML(**registro.dict())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    return db_registro

def obtener_registros(db: Session, skip: int = 0, limit: int = 1000):
    """Obtiene una lista de registros desde la base de datos con paginación.

    Args:
        db (Session): Sesión de SQLAlchemy para realizar la consulta.
        skip (int, optional): Número de registros a omitir desde el inicio. Por defecto es 0.
        limit (int, optional): Número máximo de registros a retornar. Por defecto es 1000.

    Returns:
        List[models.RegistroML]: Lista de objetos con los registros obtenidos.
    """
    return db.query(models.RegistroML).offset(skip).limit(limit).all()
