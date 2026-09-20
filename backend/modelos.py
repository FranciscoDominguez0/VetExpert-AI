from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class Condicion(BaseModel):
    hecho: str
    operador: Literal["igual", "distinto", "mayor", "mayor_igual", "menor", "menor_igual", "en"]
    valor: Any


class ResultadoRegla(BaseModel):
    hecho: str
    valor: Any


class Regla(BaseModel):
    id: str = Field(pattern=r"^R\d{3}$")
    categoria: str
    especies_aplicables: list[str] = Field(min_length=1)
    descripcion: str
    condiciones: list[Condicion] = Field(min_length=1)
    resultados: list[ResultadoRegla] = Field(min_length=1)
    recomendacion: str
    prioridad: int = Field(ge=1, le=10)
    explicacion: str
    fuente: str
    generada_por: str = "gemini"
    estado: Literal["activa", "inactiva"] = "activa"


class BaseReglas(BaseModel):
    version: str
    fecha_generacion: str
    modelo: str
    cantidad: int
    estado: str = "activa"
    reglas: list[Regla] = Field(min_length=20)

    @model_validator(mode="after")
    def validar_ids(self):
        ids = [r.id for r in self.reglas]
        if len(ids) != len(set(ids)):
            raise ValueError("Hay identificadores de reglas repetidos")
        self.cantidad = len(self.reglas)
        return self


class ConsultaEntrada(BaseModel):
    nombre_animal: str = Field(min_length=1, max_length=80)
    especie: str = Field(min_length=1, max_length=40)
    raza: str | None = Field(default=None, max_length=60)
    edad: float | None = Field(default=None, ge=0, le=150)
    peso: float | None = Field(default=None, gt=0, le=5000)
    hechos: dict[str, Any]


class GenerarReglasEntrada(BaseModel):
    cantidad: int = Field(default=30, ge=20, le=60)
    reemplazar: bool = True

