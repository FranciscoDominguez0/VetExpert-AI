import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "datos" / "vetexpert.db"


def conectar():
    DB.parent.mkdir(exist_ok=True)
    conexion = sqlite3.connect(DB)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar():
    with conectar() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nombre_animal TEXT NOT NULL,
            especie TEXT NOT NULL,
            entrada TEXT NOT NULL,
            resultado TEXT NOT NULL
        )""")


def guardar(nombre: str, especie: str, entrada: dict, resultado: dict) -> tuple[int, str]:
    fecha = datetime.now(timezone.utc).isoformat()
    with conectar() as con:
        cursor = con.execute(
            "INSERT INTO consultas(fecha,nombre_animal,especie,entrada,resultado) VALUES(?,?,?,?,?)",
            (fecha, nombre, especie, json.dumps(entrada, ensure_ascii=False), json.dumps(resultado, ensure_ascii=False)),
        )
        return cursor.lastrowid, fecha


def listar():
    with conectar() as con:
        return [dict(f) for f in con.execute(
            "SELECT id,fecha,nombre_animal,especie FROM consultas ORDER BY id DESC"
        ).fetchall()]


def obtener(consulta_id: int):
    with conectar() as con:
        fila = con.execute("SELECT * FROM consultas WHERE id=?", (consulta_id,)).fetchone()
    if not fila:
        return None
    dato = dict(fila)
    dato["entrada"] = json.loads(dato["entrada"])
    dato["resultado"] = json.loads(dato["resultado"])
    return dato

