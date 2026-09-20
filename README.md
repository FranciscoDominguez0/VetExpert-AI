# VetExpert AI

Sistema experto veterinario multiespecie con FastAPI, NiceGUI, SQLite, Experta,
reglas JSON y generación automática de reglas mediante Gemini.

> Proyecto académico de orientación y triaje. No sustituye el diagnóstico de un veterinario.

## Requisito importante

Utiliza **Python 3.11 de 64 bits**. No se recomienda Python 3.13 porque Experta
1.9.4 y su dependencia `frozendict` son antiguas.

## Instalar en Ubuntu o WSL2

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv git unzip
cd VetExpert-AI
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` y coloque su clave de Gemini:

```env
GEMINI_API_KEY=su_clave_real
GEMINI_MODEL=gemini-2.5-flash
API_URL=http://127.0.0.1:8000
```

## Instalar en Windows

Instale Python 3.11 y ejecute en PowerShell:

```powershell
cd VetExpert-AI
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Ejecutar

Terminal 1:

```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2:

```bash
source .venv/bin/activate
python frontend/main.py
```

En Windows use `.\.venv\Scripts\Activate.ps1` en cada terminal.

- Interfaz: http://localhost:8080
- API: http://localhost:8000/docs

Primero abra **Reglas IA** y pulse **Generar reglas con Gemini**. Después podrá
crear evaluaciones.

## Pruebas

```bash
pytest -q
```

## Estructura

```text
VetExpert-AI/
├── backend/
│   ├── main.py
│   ├── modelos.py
│   ├── motor.py
│   ├── repositorio.py
│   ├── gemini_service.py
│   └── reglas.json
├── frontend/main.py
├── tests/test_motor.py
├── datos/
├── .env.example
├── requirements.txt
└── README.md
```

## Nota sobre el enunciado

El enunciado original pide un motor propio. Aquí se usa Experta porque fue un
requisito adicional del proyecto. `backend/motor.py` actúa como adaptador propio:
lee el JSON, valida operadores sin `eval`, crea reglas dinámicas de Experta y
registra la traza y las contradicciones.
