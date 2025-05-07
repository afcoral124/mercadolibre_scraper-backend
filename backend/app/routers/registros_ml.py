from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from .. import crud, schemas, models
from ..db.connection import get_db

router = APIRouter(
    prefix="/registros",
    tags=["registros_ml"]
)

@router.post("/", response_model=schemas.Registro, status_code=status.HTTP_201_CREATED)
def crear_registro(registro: schemas.RegistroCreate, db: Session = Depends(get_db)):
    """Crea un nuevo registro en la base de datos desde un endpoint POST.

    Args:
        registro (schemas.RegistroCreate): Datos del registro a crear enviados por el cliente.
        db (Session, optional): Sesión de base de datos inyectada por FastAPI.

    Returns:
        schemas.Registro: Registro creado, incluyendo el ID asignado.

    Raises:
        HTTPException: 409 si el enlace del artículo ya existe.
        HTTPException: 500 si ocurre un error inesperado de base de datos.
    """
    try:
        return crud.crear_registro(db=db, registro=registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Este enlace_articulo ya fue registrado previamente."
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error inesperado en el servidor: {str(e)}"
        )


@router.get("/", response_model=List[schemas.Registro])
def obtener_registros(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """Obtiene registros de la base de datos desde un endpoint GET con paginación.

    Args:
        skip (int, optional): Número de registros a omitir. Por defecto es 0.
        limit (int, optional): Número máximo de registros a retornar. Por defecto es 1000.
        db (Session, optional): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[schemas.Registro]: Lista de registros obtenidos desde la base de datos.
    """
    return db.query(models.RegistroML).offset(skip).limit(limit).all()