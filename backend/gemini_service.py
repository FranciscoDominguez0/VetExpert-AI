import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from backend.modelos import BaseReglas

load_dotenv()
RUTA_REGLAS = Path(__file__).resolve().parent / "reglas.json"

ESPECIES = [
    "perro", "gato", "ave", "conejo", "roedor", "reptil", "caballo",
    "bovino", "porcino", "caprino", "ovino", "cualquier_especie",
]
HECHOS = [
    "edad", "peso", "vomitos", "diarrea", "come_normalmente", "bebe_agua",
    "fiebre", "dificultad_respiratoria", "tos", "estornudos", "sangrado",
    "puede_caminar", "consciente", "convulsiones", "herida_visible",
    "secrecion_nasal", "secrecion_ocular", "inflamacion", "dolor", "debilidad",
    "abdomen_distendido", "picazon", "perdida_pelo", "salivacion_excesiva",
    "dificultad_orinar", "cambio_color_orina", "exposicion_toxico",
    "parasitos_visibles", "perdida_peso", "perdida_liquidos",
    "sindrome_digestivo", "sindrome_respiratorio", "sindrome_cutaneo",
    "sindrome_neurologico", "sindrome_urinario", "sindrome_traumatico",
    "posible_gastroenteritis", "posible_deshidratacion", "posible_parasitosis",
    "posible_infeccion_respiratoria", "posible_neumonia", "posible_dermatitis",
    "posible_infestacion_externa", "posible_lesion_traumatica",
    "posible_fractura", "posible_intoxicacion", "posible_problema_neurologico",
    "posible_obstruccion_digestiva", "posible_infeccion_urinaria",
    "posible_enfermedad_sistemica",
]


def _prompt(cantidad: int) -> str:
    return f"""
Genera una base de conocimiento para un sistema experto veterinario académico
multiespecie. Produce exactamente {cantidad} reglas distintas que identifiquen
posibles enfermedades o condiciones a partir de síntomas. Todas las conclusiones
deben expresarse como hipótesis con hechos cuyo nombre comience por "posible_".
No indiques medicamentos, dosis ni tratamientos.

Especies permitidas: {ESPECIES}
Hechos permitidos: {HECHOS}
Operadores permitidos: igual, distinto, mayor, mayor_igual, menor, menor_igual, en.
Cada id debe ir desde R001 en adelante, sin repetirse. Incluye al menos dos cadenas
de tres reglas usando los hechos intermedios "sindrome_...". La prioridad de la
regla será de 1 a 10 y solo controla el orden interno de inferencia. No generes
resultados como emergencia, urgente, atención prioritaria, nivel de atención u
observación recomendada. Cada regla final debe producir una posible enfermedad.
Las recomendaciones deben solicitar confirmación mediante evaluación veterinaria.
Incluye una fuente veterinaria identificable por regla. Devuelve solamente JSON válido.

Devuelve un objeto JSON con esta estructura exacta:

{{
  "reglas": [
    {{
      "id": "R001",
      "categoria": "enfermedad_digestiva",
      "especies_aplicables": ["cualquier_especie"],
      "descripcion": "Descripción corta",
      "condiciones": [
        {{
          "hecho": "sindrome_digestivo",
          "operador": "igual",
          "valor": true
        }}
      ],
      "resultados": [
        {{
          "hecho": "posible_gastroenteritis",
          "valor": true
        }}
      ],
      "recomendacion": "Solicitar evaluación veterinaria para confirmar o descartar la condición.",
      "prioridad": 7,
      "explicacion": "La combinación de signos digestivos es compatible con esta posible condición.",
      "fuente": "Fuente veterinaria identificable",
      "generada_por": "gemini",
      "estado": "activa"
    }}
  ]
}}

No agregues Markdown, comentarios ni texto fuera del JSON.
"""


def generar_reglas(cantidad: int = 30) -> BaseReglas:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    cliente = genai.Client(api_key=api_key)
    respuesta = cliente.models.generate_content(
        model=modelo,
        contents=_prompt(cantidad),
        config={
            "response_mime_type": "application/json",
            "temperature": 0.8,
        },
    )
    contenido = json.loads(respuesta.text)
    if isinstance(contenido, list):
        reglas = contenido
    else:
        reglas = contenido.get("reglas", [])
    datos = {
        "version": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "fecha_generacion": datetime.now(timezone.utc).isoformat(),
        "modelo": modelo,
        "cantidad": len(reglas),
        "estado": "activa",
        "reglas": reglas,
    }
    base = BaseReglas.model_validate(datos)
    temporal = RUTA_REGLAS.with_suffix(".tmp")
    temporal.write_text(base.model_dump_json(indent=2), encoding="utf-8")
    temporal.replace(RUTA_REGLAS)
    return base
