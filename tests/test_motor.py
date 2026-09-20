from backend import compat  # noqa: F401
from experta import Fact

from backend.modelos import Regla
from backend.motor import comparar, crear_motor


def test_operadores():
    assert comparar(True, "igual", True)
    assert comparar(39.5, "mayor", 39)
    assert comparar("ave", "en", ["ave", "reptil"])
    assert not comparar(2, "mayor", 5)


def test_regla_json_convertida_a_experta():
    regla = Regla(
        id="R001", categoria="prueba", especies_aplicables=["cualquier_especie"],
        descripcion="Detectar prioridad",
        condiciones=[{"hecho": "vomitos", "operador": "igual", "valor": True}],
        resultados=[{"hecho": "atencion_prioritaria", "valor": True}],
        recomendacion="Consultar al veterinario", prioridad=5,
        explicacion="Regla de prueba", fuente="Prueba automatizada",
    )
    Motor = crear_motor([regla])
    motor = Motor()
    motor.reset()
    motor.hechos_actuales = {"vomitos": True}
    motor.declare(Fact(nombre="vomitos", valor=True))
    motor.run()
    assert motor.hechos_actuales["atencion_prioritaria"] is True
    assert motor.traza[0]["regla"] == "R001"
