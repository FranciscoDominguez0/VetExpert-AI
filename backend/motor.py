import json
from pathlib import Path
from typing import Any

from backend import compat  # noqa: F401; debe cargarse antes de Experta
from experta import Fact, KnowledgeEngine, P, Rule

from backend.modelos import BaseReglas, Regla

RUTA_REGLAS = Path(__file__).resolve().parent / "reglas.json"


def comparar(actual: Any, operador: str, esperado: Any) -> bool:
    try:
        return {
            "igual": lambda: actual == esperado,
            "distinto": lambda: actual != esperado,
            "mayor": lambda: actual > esperado,
            "mayor_igual": lambda: actual >= esperado,
            "menor": lambda: actual < esperado,
            "menor_igual": lambda: actual <= esperado,
            "en": lambda: actual in esperado,
        }[operador]()
    except (TypeError, KeyError):
        return False


def cargar_reglas() -> list[Regla]:
    datos = json.loads(RUTA_REGLAS.read_text(encoding="utf-8"))
    if not datos.get("reglas"):
        raise RuntimeError("La base está vacía. Genere las reglas con Gemini.")
    return BaseReglas.model_validate(datos).reglas


def crear_motor(reglas: list[Regla]):
    def iniciar(self):
        KnowledgeEngine.__init__(self)
        self.hechos_actuales = {}
        self.traza = []
        self.recomendaciones = []
        self.contradicciones = []

    def agregar_resultado(self, regla: Regla):
        producidos = []
        for resultado in regla.resultados:
            anterior = self.hechos_actuales.get(resultado.hecho, None)
            if resultado.hecho in self.hechos_actuales and anterior != resultado.valor:
                self.contradicciones.append({
                    "hecho": resultado.hecho,
                    "existente": anterior,
                    "nuevo": resultado.valor,
                    "regla": regla.id,
                })
                continue
            if resultado.hecho not in self.hechos_actuales:
                self.hechos_actuales[resultado.hecho] = resultado.valor
                self.declare(Fact(nombre=resultado.hecho, valor=resultado.valor))
                producidos.append(resultado.model_dump())
        if producidos:
            self.recomendaciones.append(regla.recomendacion)
            self.traza.append({
                "regla": regla.id,
                "descripcion": regla.descripcion,
                "explicacion": regla.explicacion,
                "hechos_producidos": producidos,
            })

    atributos = {
        "__init__": iniciar,
        "agregar_resultado": agregar_resultado,
    }

    for regla in reglas:
        patrones = []
        for condicion in regla.condiciones:
            op, esperado = condicion.operador, condicion.valor
            predicado = P(lambda actual, op=op, esperado=esperado: comparar(actual, op, esperado))
            patrones.append(Fact(nombre=condicion.hecho, valor=predicado))

        def accion(self, regla=regla):
            self.agregar_resultado(regla)

        accion.__name__ = f"activar_{regla.id.lower()}"
        atributos[accion.__name__] = Rule(*patrones, salience=regla.prioridad)(accion)
    return type("MotorDinamico", (KnowledgeEngine,), atributos)


def inferir(especie: str, hechos: dict[str, Any]) -> dict[str, Any]:
    reglas = [
        r for r in cargar_reglas()
        if r.estado == "activa" and (especie in r.especies_aplicables or "cualquier_especie" in r.especies_aplicables)
    ]
    Motor = crear_motor(reglas)
    motor = Motor()
    motor.reset()
    iniciales = {"especie": especie, **hechos}
    motor.hechos_actuales.update(iniciales)
    for nombre, valor in iniciales.items():
        if valor != "desconocido" and valor is not None:
            motor.declare(Fact(nombre=nombre, valor=valor))
    motor.run()
    derivados = {k: v for k, v in motor.hechos_actuales.items() if k not in iniciales}
    conclusiones = {
        k: v for k, v in derivados.items()
        if k.startswith("posible_") and v is True
    }
    enfermedades_posibles = [
        {
            "codigo": nombre,
            "nombre": nombre.removeprefix("posible_").replace("_", " ").title(),
        }
        for nombre in conclusiones
    ]
    return {
        "hechos_originales": iniciales,
        "hechos_derivados": derivados,
        "conclusiones": conclusiones,
        "enfermedades_posibles": enfermedades_posibles,
        "recomendaciones": list(dict.fromkeys(motor.recomendaciones)),
        "reglas_activadas": motor.traza,
        "contradicciones": motor.contradicciones,
        "estado": "completada" if enfermedades_posibles else "evidencia_insuficiente",
    }
