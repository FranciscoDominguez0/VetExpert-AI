import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

from backend.gemini_service import generar_reglas
from backend.modelos import ConsultaEntrada, GenerarReglasEntrada
from backend.motor import inferir
from backend.repositorio import guardar, inicializar, listar, obtener

RUTA_REGLAS = Path(__file__).resolve().parent / "reglas.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar()
    yield


app = FastAPI(title="VetExpert AI API", version="1.0.0", lifespan=lifespan)


@app.get("/salud")
def salud():
    return {"estado": "disponible"}


@app.get("/reglas")
def reglas():
    return json.loads(RUTA_REGLAS.read_text(encoding="utf-8"))


@app.post("/reglas/generar")
def generar(datos: GenerarReglasEntrada):
    try:
        return generar_reglas(datos.cantidad)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudieron generar reglas: {exc}") from exc


@app.post("/consultas")
def consultar(datos: ConsultaEntrada):
    try:
        hechos = {
            **datos.hechos,
            "edad": datos.edad,
            "peso": datos.peso,
        }
        resultado = inferir(datos.especie.lower(), hechos)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    entrada = datos.model_dump()
    consulta_id, fecha = guardar(datos.nombre_animal, datos.especie, entrada, resultado)
    return {"id": consulta_id, "fecha": fecha, **resultado}


@app.get("/consultas")
def historial():
    return listar()


@app.get("/consultas/{consulta_id}")
def detalle(consulta_id: int):
    consulta = obtener(consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consulta
