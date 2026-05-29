# ══════════════════════════════════════════════════════════════════════════════
# 🦦 Nutri IA — Backend FastAPI
# Sirve el frontend React y llama a HuggingFace (Llama 3 + FLUX.1-schnell)
# Autora: Carolhina Real Vega | ID: 038330 | No Clase: 5397
# ══════════════════════════════════════════════════════════════════════════════

import os, base64, io, logging, requests
from pathlib import Path
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ── API Key (Secret de HF Spaces o variable de entorno) ───────────────────────
HF_TOKEN = os.environ.get("Nutri_IA", "")

TEXTO_ENDPOINT  = "https://router.huggingface.co/v1/chat/completions"
MODELO_TEXTO    = "meta-llama/Meta-Llama-3-8B-Instruct:novita"
IMAGEN_ENDPOINT = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
HEADERS_JSON    = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

app = FastAPI(title="Nutri IA")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Modelos de datos ───────────────────────────────────────────────────────────
class PerfilPaciente(BaseModel):
    condicion: str
    alergias: str = ""
    prohibiciones: str = ""
    preferencias: str = ""

# ── Manejo de errores ──────────────────────────────────────────────────────────
class APIError(Exception):
    pass

def verificar_respuesta(response, ctx):
    c = response.status_code
    if c == 200: return
    try: detalle = response.json().get("error", response.text[:200])
    except: detalle = response.text[:200]
    if c == 429: raise APIError(f"[{ctx}] Rate limit (429). Reintentando...")
    if c >= 500: raise APIError(f"[{ctx}] Error servidor ({c}): {detalle}")
    if c == 401: raise HTTPException(401, f"[{ctx}] Token inválido. Verifica el Secret 'Nutri_IA'.")
    if c == 403: raise HTTPException(403, f"[{ctx}] Acceso denegado. Acepta los términos del modelo.")
    raise HTTPException(c, f"[{ctx}] Error {c}: {detalle}")

# ── Prompts (idénticos al notebook) ───────────────────────────────────────────
SYSTEM_PROMPT = (
    "Eres Nutri IA, un chef clínico y nutricionista certificado con 15 años de experiencia "
    "diseñando dietas terapéuticas para pacientes con condiciones médicas complejas. "
    "Tus recetas deben ser deliciosas, 100% seguras para la condición indicada "
    "y apoyadas en evidencia nutricional. Siempre redactas en un idioma y lenguaje claro para el paciente. "
    "Jamás sugieres ingredientes prohibidos, ni siquiera en pequeñas cantidades."
)

FEW_SHOT = """es solo un EJEMPLO DE REFERENCIA, procesa EXCLUSIVAMENTE los casos reales
ENTRADA: {"condicion":"celiaquía","alergias":"mariscos","prohibiciones":"gluten","preferencias":"dulce"}
SALIDA ESPERADA:
## Sushi Bowl de Salmón con Mango
**Seguro para:** celiaquía
**Tiempo:** 30 min | **Porciones:** 2 | **Calorías:** ~420 kcal
### Alertas de seguridad verificadas
- 100% libre de gluten
### Ingredientes
- 160g arroz blanco japonés
- 160g salmón fresco
### Preparación Paso a Paso
**1. Cocinar el arroz (15 min)** Lavar el arroz y cocinar...
### Beneficios Nutricionales por Condición
| Condición | Beneficio |
|-----------|-----------|
| Celiaquía | Sin gluten |
### Prompt Visual
Professional food photography, sushi bowl with salmon and mango, soft light, 8K, Michelin plating.
=== FIN DEL EJEMPLO ==="""

def construir_prompt(condicion, alergias, prohibiciones, preferencias):
    return f"""{FEW_SHOT}

Paciente real:
- Condición médica: {condicion}
- Alergias: {alergias or 'ninguna'}
- Ingredientes prohibidos: {prohibiciones or 'ninguno'}
- Preferencias: {preferencias or 'sin preferencia'}

Instrucción:
Paso 1 - RESTRICCIONES: Identifica todos los ingredientes a evitar.
Paso 2 - SUSTITUCIÓN: Encuentra sustitutos saludables.
Paso 3 - RECETA: Redacta la receta completa con el mismo formato del ejemplo.
Paso 4 - PROMPT VISUAL: Escribe un prompt fotográfico en inglés al final bajo "### Prompt Visual".

Responde directamente con la receta en markdown."""

# ── Motor de texto ─────────────────────────────────────────────────────────────
@retry(retry=retry_if_exception_type(APIError), stop=stop_after_attempt(3),
       wait=wait_exponential(min=2, max=10), before_sleep=before_sleep_log(logger, logging.WARNING), reraise=True)
def _texto(payload):
    r = requests.post(TEXTO_ENDPOINT, headers=HEADERS_JSON, json=payload, timeout=90)
    verificar_respuesta(r, "Texto")
    return r.json()["choices"][0]["message"]["content"]

def generar_receta(condicion, alergias, prohibiciones, preferencias):
    payload = {
        "model": MODELO_TEXTO,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": construir_prompt(condicion, alergias, prohibiciones, preferencias)},
        ],
        "max_tokens": 1500, "temperature": 0.75, "top_p": 0.7,
    }
    texto = _texto(payload)

    prompt_visual = ""
    for marcador in ["### Prompt Visual", "**Prompt Visual**", "Prompt Visual:"]:
        if marcador in texto:
            partes = texto.split(marcador, 1)
            prompt_visual = partes[1].strip().lstrip(":").strip().split("\n###")[0].replace("**", "").strip()
            texto = partes[0].strip()
            break

    if not prompt_visual:
        prompt_visual = (
            f"Professional food photography, a healthy meal for {condicion}, "
            "beautifully plated, soft natural light, wooden table, 8K, Michelin star presentation."
        )
    return texto, prompt_visual

# ── Motor de imagen ────────────────────────────────────────────────────────────
@retry(retry=retry_if_exception_type(APIError), stop=stop_after_attempt(3),
       wait=wait_exponential(min=3, max=15), before_sleep=before_sleep_log(logger, logging.WARNING), reraise=True)
def _imagen(payload):
    r = requests.post(IMAGEN_ENDPOINT, headers=HEADERS_JSON, json=payload, timeout=120)
    verificar_respuesta(r, "Imagen")
    return r

def generar_imagen(prompt_visual):
    payload = {
        "inputs": prompt_visual,
        "parameters": {
            "negative_prompt": "burnt, blurry, cartoon, watermark, low quality, dirty plate, raw meat",
            "num_inference_steps": 4, "width": 1024, "height": 1024, "guidance_scale": 0.0,
        },
    }
    try:
        r = _imagen(payload)
        ct = r.headers.get("Content-Type", "")
        if "application/json" in ct:
            data = r.json()
            b64 = (data.get("data", [{}])[0].get("b64_json") or
                   (data.get("images", [""])[0] if isinstance(data.get("images", [""])[0], str) else ""))
            if b64: return base64.b64encode(base64.b64decode(b64)).decode()
            return None
        # bytes directos
        img = Image.open(io.BytesIO(r.content))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        logger.warning(f"Imagen no generada: {e}")
        return None

# ── Rutas ──────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text(encoding="utf-8")

@app.post("/api/receta")
async def api_receta(perfil: PerfilPaciente):
    if not perfil.condicion.strip():
        raise HTTPException(400, "La condición médica es obligatoria.")
    if not HF_TOKEN:
        raise HTTPException(500, "No se encontró la API Key 'Nutri_IA'. Configúrala en los Secrets.")

    try:
        receta_texto, prompt_visual = generar_receta(
            perfil.condicion, perfil.alergias, perfil.prohibiciones, perfil.preferencias
        )
    except (APIError, Exception) as e:
        raise HTTPException(502, f"Error al generar la receta: {str(e)}")

    imagen_b64 = generar_imagen(prompt_visual)

    return JSONResponse({"receta": receta_texto, "imagen_base64": imagen_b64})

@app.get("/health")
async def health():
    return {"status": "ok", "token_configurado": bool(HF_TOKEN)}
