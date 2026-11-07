# Editar una grabación que ya existe

Esta rama implementa cortes revisados, captions, demo y aprobación. No genera B-roll ni decide por sí sola qué palabras sobran. El agente conversa, revisa el transcript/voz y prepara el plan; Python y FFmpeg ejecutan la edición.

1. En un proyecto con entorno local comprobado, ejecutar `recording-import --file TOMA`. Se conserva una copia por hash. La grabación necesita video y audio, entre 15 s y 10 minutos. Nunca editar sobre el original.
2. `recording-silences` propone intervalos acústicos. El umbral es un punto de partida, no una decisión editorial. Escuchar/revisar cada corte para proteger consonantes, respiraciones, demostraciones y pausas expresivas. Si el detector no sirve para esa toma, construir el plan con evidencia manual.
3. Obtener transcript y tiempos reales con el ASR local disponible o captions del usuario. El motor no descarga un modelo sin avisar ni inventa tiempos por repartir el texto. Ajustar los cortes a cuadros de 1/30 s y remapear los captions al reloj del montaje final.
4. Crear el JSON siguiente y ejecutar `recording-prepare --plan PLAN.json`. Cada intervalo dice qué conservar, en orden. `reason` explica el criterio. Los tiempos de captions corresponden al video ya recortado.

```json
{
  "segments": [{"start":0,"end":8},{"start":10,"end":20}],
  "reason":"La pausa 8–10 s fue revisada y no aporta a esta frase.",
  "captions":[{"start":0.2,"end":2.5,"text":"Texto real de la narración."}],
  "caption_preset":{"size_ratio":0.045,"y_ratio":0.84,"color":"#FFFFFF","outline":"#161616"}
}
```

5. `recording-demo` genera los primeros 15 segundos editados. Mostrar el MP4, incluidos cortes y captions. Si el problema importante queda después, mostrar también el tramo pertinente mediante un plan de prueba separado; no pedir aprobación de cortes que la persona no puede revisar.
6. Registrar la respuesta real con `recording-approve --decision approve --response-file RESPUESTA.txt`; solo después ejecutar `recording-full`. Un rechazo bloquea el completo. Cambiar el plan, fuente o compositor invalida la aprobación. La respuesta se registra por el agente, no autentica al humano.

Todos estos comandos aceptan `--workspace PROYECTO`. La edición mantiene el encuadre original, salida 30 fps y audio estéreo 48 kHz. Si hay rotación de cámara, primero crear una copia con orientación aplicada y conservar el original. No hacer un recorte vertical sin acordar composición. Los empalmes son cortes directos: si producen un clic, revisar el límite y preparar una transición específica; no eliminar sílabas con fades largos.

El agente entrega la toma original, plan, demo, export completo y lo que comprobó. No prometer recorte inteligente autónomo, diarización, transcripción incorporada ni calidad idéntica para cualquier grabación. Los tests usan tonos y patrones visuales, no prueban naturalidad del habla.
