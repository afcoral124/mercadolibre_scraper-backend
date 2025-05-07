from connection import get_connection

def crear_tabla_e_indice():
    """Crea la tabla 'registros_ml' y un índice único en la base de datos si no existen.

    Esta función establece una conexión a la base de datos, crea la tabla 
    'registros_ml' con sus respectivos campos y define un índice único sobre 
    el campo 'enlace_articulo' para evitar duplicados.

    No recibe parámetros ni retorna valores.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS registros_ml (
                    id SERIAL PRIMARY KEY,
                    nombre_articulo VARCHAR(255),
                    precio INT,
                    calificacion_promedio FLOAT,
                    cantidad_calificaciones INT,
                    descripcion TEXT,
                    enlace_articulo TEXT
                );
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_enlace_articulo
                ON registros_ml(enlace_articulo);
            """)
        conn.commit()

if __name__ == "__main__":
    crear_tabla_e_indice()