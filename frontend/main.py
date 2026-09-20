import os

import httpx
from dotenv import load_dotenv
from nicegui import ui

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ESPECIES = ["perro", "gato", "ave", "conejo", "roedor", "reptil", "caballo", "bovino", "porcino", "caprino", "ovino"]
SINTOMAS = [
    ("vomitos", "Vómitos"), ("diarrea", "Diarrea"),
    ("fiebre", "Fiebre"), ("dificultad_respiratoria", "Dificultad respiratoria"),
    ("tos", "Tos"), ("puede_caminar", "Puede caminar normalmente"),
    ("convulsiones", "Convulsiones"), ("herida_visible", "Herida visible"),
    ("problemas_piel", "Picazón, irritación o pérdida de pelo"),
    ("dificultad_orinar", "Dificultad para orinar"),
    ("exposicion_toxico", "Posible exposición a tóxico"),
    ("debilidad", "Debilidad o decaimiento"),
]

ETIQUETAS_HECHOS = {
    "perdida_liquidos": "Pérdida de líquidos",
    "sindrome_digestivo": "Patrón de síntomas digestivos",
    "sindrome_respiratorio": "Patrón de síntomas respiratorios",
    "sindrome_cutaneo": "Patrón de síntomas en piel",
    "sindrome_neurologico": "Patrón de síntomas neurológicos",
    "sindrome_urinario": "Patrón de síntomas urinarios",
    "sindrome_traumatico": "Patrón compatible con lesión",
}


def texto_hecho(nombre, valor):
    etiqueta = ETIQUETAS_HECHOS.get(nombre, nombre.replace("_", " ").capitalize())
    if isinstance(valor, bool):
        return etiqueta if valor else f"No presenta: {etiqueta.lower()}"
    return f"{etiqueta}: {str(valor).capitalize()}"


def mostrar_resultado(datos, contenedor):
    derivados = datos.get("hechos_derivados", {})
    enfermedades = datos.get("enfermedades_posibles", [])
    recomendaciones = datos.get("recomendaciones", [])
    reglas = datos.get("reglas_activadas", [])
    contradicciones = datos.get("contradicciones", [])
    if enfermedades:
        titulo = "Posibles enfermedades identificadas"
        mensaje = "El sistema encontró condiciones compatibles con los síntomas registrados."
        color = "bg-teal-50 border-teal-700 text-teal-900"
        icono = "diagnosis"
    else:
        titulo = "No fue posible identificar una enfermedad"
        mensaje = "La información registrada no activa suficientes reglas. Complete o revise los síntomas."
        color = "bg-grey-100 border-grey-600 text-grey-900"
        icono = "help"

    with contenedor:
        with ui.card().classes(f"w-full border-l-8 {color}"):
            with ui.row().classes("items-center no-wrap"):
                ui.icon(icono).classes("text-4xl")
                with ui.column().classes("gap-1"):
                    ui.label(titulo).classes("text-h5 font-bold")
                    ui.label(mensaje).classes("text-base")
                    ui.label(f"Evaluación #{datos.get('id')}").classes("text-sm")

        with ui.card().classes("w-full"):
            ui.label("Condiciones posibles").classes("text-h6 text-teal-900")
            if enfermedades:
                for numero, enfermedad in enumerate(enfermedades, 1):
                    with ui.row().classes("items-center gap-3"):
                        ui.badge(str(numero), color="teal")
                        ui.label(enfermedad["nombre"]).classes("text-lg font-bold")
            else:
                ui.label("No hay evidencia suficiente para proponer una condición.")

        with ui.card().classes("w-full"):
            ui.label("Hallazgos principales").classes("text-h6 text-teal-900")
            hallazgos = [
                texto_hecho(nombre, valor)
                for nombre, valor in derivados.items()
                if valor not in (False, None) and not nombre.startswith("posible_")
            ]
            if hallazgos:
                for hallazgo in hallazgos:
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("check_circle", color="teal")
                        ui.label(hallazgo)
            else:
                ui.label("No se derivaron hallazgos adicionales con los datos registrados.")

        with ui.card().classes("w-full"):
            ui.label("Recomendaciones").classes("text-h6 text-teal-900")
            if recomendaciones:
                for numero, recomendacion in enumerate(recomendaciones, 1):
                    with ui.row().classes("items-start no-wrap gap-3"):
                        ui.badge(str(numero), color="teal")
                        ui.label(recomendacion).classes("text-base")
            else:
                ui.label("No se generaron recomendaciones específicas.")

        with ui.expansion("¿Cómo llegó el sistema a este resultado?", icon="account_tree").classes("w-full bg-grey-1"):
            if reglas:
                for regla in reglas:
                    with ui.card().classes("w-full mb-2"):
                        ui.label(f"{regla['regla']} — {regla['descripcion']}").classes("font-bold text-teal-900")
                        ui.label(regla["explicacion"])
                        producidos = ", ".join(
                            texto_hecho(h["hecho"], h["valor"])
                            for h in regla.get("hechos_producidos", [])
                        )
                        if producidos:
                            ui.label(f"Determinó: {producidos}").classes("text-sm text-grey-8")
            else:
                ui.label("Ninguna regla fue activada.")

        if contradicciones:
            with ui.expansion("Resultados incompatibles detectados", icon="rule").classes("w-full bg-blue-1"):
                ui.label(
                    "Algunas reglas intentaron asignar valores diferentes al mismo hecho. "
                    "El sistema conservó el primer resultado obtenido y registró el conflicto."
                )
                for contradiccion in contradicciones:
                    ui.label(
                        f"{contradiccion['regla']} propuso “{contradiccion['nuevo']}” para "
                        f"{contradiccion['hecho']}, pero se mantuvo “{contradiccion['existente']}”."
                    ).classes("text-sm")

        ui.label(
            "Las condiciones mostradas son hipótesis académicas y deben ser confirmadas por un veterinario."
        ).classes("w-full text-center text-caption text-grey-7 mt-2")


def encabezado():
    with ui.header().classes("bg-teal-800"):
        ui.label("VetExpert AI").classes("text-h5")
        ui.link("Inicio", "/").classes("text-white")
        ui.link("Nueva consulta", "/consulta").classes("text-white")
        ui.link("Historial", "/historial").classes("text-white")
        ui.link("Reglas IA", "/reglas").classes("text-white")


@ui.page("/")
def inicio():
    encabezado()
    with ui.column().classes("w-full max-w-4xl mx-auto p-8"):
        ui.label("Sistema experto veterinario multiespecie").classes("text-h3 text-teal-900")
        ui.markdown("Registra los síntomas de un animal para obtener una orientación inicial basada en reglas. **No sustituye la evaluación de un veterinario.**")
        ui.button("Nueva evaluación", on_click=lambda: ui.navigate.to("/consulta"), icon="pets")


@ui.page("/consulta")
def consulta():
    encabezado()
    valores = {}
    with ui.column().classes("w-full max-w-5xl mx-auto p-6"):
        ui.label("Evaluación veterinaria").classes("text-h4 text-teal-900")
        ui.label("Complete los datos básicos y responda 12 preguntas sobre los síntomas.").classes("text-grey-7")
        with ui.card().classes("w-full"):
            ui.label("Datos del animal").classes("text-h6 text-teal-900")
            with ui.row().classes("w-full"):
                nombre = ui.input("Nombre del animal").classes("grow")
                especie = ui.select(ESPECIES, label="Especie").classes("grow")
                edad = ui.number("Edad", min=0).classes("grow")
                peso = ui.number("Peso en kg", min=0.01).classes("grow")
        with ui.card().classes("w-full"):
            ui.label("Síntomas observados").classes("text-h6 text-teal-900")
            ui.label("Seleccione Sí, No o Desconocido en cada pregunta.").classes("text-sm text-grey-7")
            with ui.grid(columns=2).classes("w-full gap-4"):
                for clave, etiqueta in SINTOMAS:
                    valores[clave] = ui.select(
                        {"desconocido": "Desconocido", "si": "Sí", "no": "No"},
                        value="desconocido", label=etiqueta,
                    ).classes("w-full")
        resultado = ui.column().classes("w-full")

        async def evaluar():
            if not nombre.value or not especie.value:
                ui.notify("Nombre y especie son obligatorios", type="warning")
                return
            boton.disable()
            resultado.clear()
            try:
                async with httpx.AsyncClient(timeout=30) as cliente:
                    respuesta = await cliente.post(f"{API_URL}/consultas", json={
                        "nombre_animal": nombre.value, "especie": especie.value,
                        "edad": edad.value, "peso": peso.value,
                        "hechos": {
                            k: True if c.value == "si" else False if c.value == "no" else "desconocido"
                            for k, c in valores.items()
                        },
                    })
                    respuesta.raise_for_status()
                    datos = respuesta.json()
                with resultado:
                    ui.label("Resultado de la evaluación").classes("text-h4 text-teal-900")
                mostrar_resultado(datos, resultado)
            except httpx.ConnectError:
                ui.notify("La API no está disponible", type="negative")
            except httpx.HTTPStatusError as exc:
                try:
                    detalle = exc.response.json().get("detail", exc.response.text)
                except ValueError:
                    detalle = exc.response.text
                ui.notify(str(detalle), type="negative")
            finally:
                boton.enable()

        boton = ui.button("Evaluar", on_click=evaluar, icon="medical_services")


@ui.page("/historial")
async def historial():
    encabezado()
    with ui.column().classes("w-full max-w-5xl mx-auto p-6"):
        ui.label("Historial de consultas").classes("text-h4")
        try:
            async with httpx.AsyncClient(timeout=10) as cliente:
                filas = (await cliente.get(f"{API_URL}/consultas")).json()
            ui.table(columns=[
                {"name": "id", "label": "ID", "field": "id"},
                {"name": "fecha", "label": "Fecha", "field": "fecha"},
                {"name": "nombre_animal", "label": "Animal", "field": "nombre_animal"},
                {"name": "especie", "label": "Especie", "field": "especie"},
            ], rows=filas, row_key="id").classes("w-full")
        except Exception:
            ui.label("No fue posible cargar el historial.").classes("text-red")


@ui.page("/reglas")
def reglas():
    encabezado()
    with ui.column().classes("w-full max-w-5xl mx-auto p-6"):
        ui.label("Generación de conocimiento con Gemini").classes("text-h4 text-teal-900")
        ui.label(
            "Gemini creará reglas veterinarias en formato JSON. El proceso puede tardar entre 20 y 90 segundos."
        ).classes("text-grey-7")
        with ui.card().classes("w-full"):
            ui.label("Configuración").classes("text-h6")
            cantidad = ui.number("Cantidad de reglas", value=20, min=20, max=60).classes("w-64")
        estado = ui.row().classes("items-center gap-3 p-4 bg-blue-50 rounded w-full")
        with estado:
            ui.spinner("dots", size="lg", color="teal")
            texto_estado = ui.label("Gemini está generando y organizando las reglas...").classes("text-teal-900 font-bold")
        estado.set_visibility(False)
        salida = ui.column().classes("w-full")

        async def generar():
            boton.disable()
            salida.clear()
            estado.set_visibility(True)
            texto_estado.set_text("Gemini está generando y organizando las reglas...")
            ui.notify("Generación iniciada. Espere mientras Gemini prepara el JSON.", type="info")
            try:
                async with httpx.AsyncClient(timeout=120) as cliente:
                    respuesta = await cliente.post(f"{API_URL}/reglas/generar", json={"cantidad": int(cantidad.value), "reemplazar": True})
                    respuesta.raise_for_status()
                    datos = respuesta.json()
                with salida:
                    with ui.card().classes("w-full bg-green-50 border-l-4 border-green-600"):
                        ui.icon("check_circle", color="green").classes("text-3xl")
                        ui.label("Reglas generadas correctamente").classes("text-h6 text-green-900")
                        ui.label(f"Versión {datos['version']} · {datos['cantidad']} reglas disponibles")
                    with ui.expansion("Ver JSON generado", icon="data_object").classes("w-full"):
                        ui.json_editor({"content": {"json": datos}}).classes("w-full")
                ui.notify("La base de conocimiento fue actualizada.", type="positive")
            except Exception as exc:
                ui.notify(f"Error al generar reglas: {exc}", type="negative")
            finally:
                estado.set_visibility(False)
                boton.enable()

        boton = ui.button("Generar reglas con Gemini", on_click=generar, icon="auto_awesome")


ui.run(host="127.0.0.1", port=8080, title="VetExpert AI", reload=False)
