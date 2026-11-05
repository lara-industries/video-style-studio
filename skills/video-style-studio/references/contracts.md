# Contrato de archivos y comandos

Todos los comandos se ejecutan con el Python del entorno de la skill:

```sh
python scripts/studio.py COMANDO --workspace /ruta/a/proyecto
```

`--help` es la referencia exacta de argumentos. El proyecto contiene `project.json`, assets inmutables por hash, cuadros y renders. Su `.gitignore` evita que material del usuario acabe en el repositorio. Los paths internos son relativos y se rechazan escapes por `..`/symlink. No mover el proyecto mientras se escribe.

## Entorno

`confirm-environment --evidence environment.json` acepta:

```json
{"execution_location":"user-desktop","source":"user-confirmation","evidence":"Respuesta literal del usuario confirmando que la sesión puede controlar sus archivos y terminal locales."}
```

Usar `runtime-attestation` solo si una capacidad del runtime lo demuestra; no usar esa etiqueta para una inferencia. `doctor` comprueba dependencias y deja ubicación/app desconocidas.

`consent --scope third-party-install|elevenlabs-generation|scrapecreators-request --decision approve|reject --response-file answer.txt` conserva el texto real. Es un registro del agente, no autenticación del humano. No interpretar respuestas ambiguas como aprobación.

## Análisis

Tras `capture`, `transcript`/`provider-transcript`/`transcribe`, `extract` y `burst`, el agente escribe:

```json
{
  "source_sha256": "hash de reference.media",
  "analyst": "agente/runtime real",
  "literal_reading": {"title": true, "description": true, "transcript": true},
  "reviewed_contact_sheets": ["rutas de todas las hojas realmente vistas"],
  "reviewed_native_frames": ["rutas de cuadros nativos realmente vistos"],
  "visual_type": "motion-graphics",
  "compatibility": {"supported": true, "stack": "pillow2d", "limitations": []},
  "audio_review": {"mode": "perceptual, measurements o unavailable", "findings": "evidencia real"},
  "limitations": ["Cobertura real y detalles que no fue posible comprobar"],
  "rules": [
    {"aspect":"motion","status":"observed","evidence":"Cuadros 48–62; archivo...","rule":"Describe la medida y su consecuencia"}
  ]
}
```

Son obligatorios los aspectos `composition`, `palette`, `typography`, `camera`, `motion`, `narrative`, `sound`. Los estados son `observed`, `inferred`, `proposed`. Cada regla necesita evidencia; no llenar los siete con frases genéricas. `analyze --file analysis.json` comprueba vínculo/cobertura declarada; no puede certificar que un agente haya mirado los archivos. La declaración sigue siendo responsabilidad del agente.

## Estilo reutilizable

```json
{
  "name":"Nombre elegido por el usuario",
  "source_sha256":"hash de la referencia",
  "renderer":"pillow2d",
  "rules":[{"aspect":"motion","rule":"Reglas medidas propias"}],
  "caption_preset":{"size_ratio":0.045,"y_ratio":0.84,"color":"#FFFFFF","outline":"#161616"}
}
```

Añadir los parámetros que la escena necesite: paleta, ritmos, márgenes, curvas, materiales, zonas protegidas. No incrustar un rostro/voz en estas reglas. `style --file` lo guarda; `export-style --output` exporta solo reglas. `reuse-style --from-workspace ANTERIOR --workspace NUEVO` copia evidencia y estilo a un proyecto sin voz/guion/aprobaciones. Permite otra historia sin volver a pagar una captura.

## Historia, escena y audio

`voice-file --file ...` importa audio. `voice-eleven --text-file ...` genera una vez tras consentimiento y preserva la respuesta. `prepare` requiere ambos estilo y voz y recibe:

```json
{
  "text":"La narración exacta y completa.",
  "beats":[{"start":0,"end":3,"visible_action":"Acción concreta","meaning":"Qué entiende el espectador"}],
  "captions":[{"start":0,"end":3,"text":"La narración exacta y completa."}],
  "events":[{"frame":36,"kind":"impact","gain":0.12}]
}
```

Captions consecutivos, sin solaparse, dentro de la duración de voz y con texto total igual al guion. Los tiempos los obtiene/revisa el agente sobre el audio real, no por dividir palabras uniformemente. El ejemplo automatizado usa tiempos de fixture y lo declara. `events` admite `impact`, `tick`, `whoosh`, ganancia 0–0.5; son sonidos procedurales sencillos originales. El mismo `frame` guía el contacto visual.

La escena `.py` define `render_frame(t, width, height, context)` y devuelve una imagen PIL de ese tamaño. `context` contiene estilo, guion, eventos, fps y ruta de proyecto. Código local escrito/revisado por el agente, nunca extraído de una referencia. El worker quita llaves del entorno, pero **no es un sandbox de código**. Puede usar assets autorizados del proyecto y librerías ya disponibles. El ejemplo `examples/scene.py` del repositorio es una demostración genérica, no un estilo del autor.

`render-demo` genera15 s y valida cuadro/duración/audio/decodificación completa. Los captions los compone la librería sobre la escena. `approve-demo` vincula la respuesta al hash del archivo y todas sus entradas. `render-full` verifica el vínculo vigente. `status` comprueba vigencia, no solo existencia de claves. Cambiar escena/voz/guion/estilo/referencia/settings invalida aprobación; la voz corta deja un hold explícito hasta15 s.

No hay instalación implícita, generador remoto oculto, borrado de originales, publicación ni envío. Las URL firmadas y media de fuentes pertenecen al proyecto privado del usuario, no al paquete público.
