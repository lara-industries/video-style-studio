---
name: video-style-studio
description: Analizar un video de referencia, guardar sus reglas de animación y producir una historia original con voz, captions y una demo de 15 segundos antes del video completo. Para agentes con archivos y ejecución local; verifica esas capacidades antes de instalar o producir.
---

# Video Style Studio

Habla en español por defecto y guía a una persona que no necesita saber editar ni programar. El agente hace el trabajo técnico. No le pidas rellenar un formulario ni ejecutar todos los comandos a mano.

Invocación: «Usa video-style-studio. Crea un video inspirado en <URL> que explique <idea>». Si el estilo ya existe: «Usa video-style-studio con el estilo <nombre> y cuenta <idea>».

La entrega es un MP4 local reproducible, su voz conservada y el proyecto. La skill no es un servicio alojado, no instala un servidor MCP y no publica, envía mensajes ni gestiona cuentas. No incluye estilos de un creador, retratos, voces clonadas, música o referencias de terceros. Cada usuario construye su biblioteca.

## 1. Recibir y comprobar

Abre con algo como: «Primero compruebo que puedo trabajar en tu computador. Después analizamos tu referencia, añadimos la voz y te enseño una demo de 15 segundos. Tú decides si seguimos con el video completo. Antes de instalar algo te diré qué es y te pediré autorización».

Lee [installation.md](references/installation.md). Ejecuta `scripts/studio.py doctor` si existe una herramienta real de ejecución. El resultado prueba archivos/procesos/dependencias en **ese runtime**. No demuestra qué app tiene abierta la persona, si trabaja en navegador o si el runtime es su computador. No lo deduzcas de procesos, nombres del sistema o user-agent.

- Evidencia del runtime que confirma acceso local al computador: conserva esa evidencia.
- Runtime cuya ubicación no está clara: pregunta si esta sesión tiene habilitado trabajo local sobre su computador y un directorio local accesible. Registra su respuesta como `user-confirmation`, no como detección automática.
- Sin terminal/archivos locales: explica el límite y guía hacia una sesión local compatible. Puedes preparar idea/guion, pero no afirmar instalación, descarga ni render.
- Una app de escritorio sin herramientas habilitadas tampoco basta. ChatGPT con trabajo local habilitado puede servir; un chat web estándar o un contenedor remoto no equivalen al computador del usuario. [Compatibilidad](references/compatibility.md).

Muestra qué falta, el plan exacto por sistema y el espacio necesario. **No ejecutes instalación de terceros hasta recibir autorización explícita**, salvo que ya exista en esta conversación. No pidas la misma aprobación de nuevo. Esta skill solo copia su carpeta al instalarse; las dependencias se instalan con los comandos aprobados. Nunca solicites desactivar la seguridad del equipo.

## 2. Crear o recuperar el proyecto

Usa una carpeta nueva fuera del código de la skill. `init --workspace RUTA --reference-url URL` exige el enlace de origen. Consulta `status` al reanudar. Las entradas se guardan por hash; no sobrescribas originales.

Si existe el estilo pedido, recupera su proyecto y usa `reuse-style --from-workspace ANTERIOR --workspace NUEVO`. Copia reglas y evidencia, **no** voz, guion, permisos ni aprobaciones anteriores. El enlace original sigue guardado. Si no existe, explica: «Primero vamos a construir ese estilo con tu referencia y luego lo usaremos para tu idea».

No asumas quién es la persona ni inventes su historia. Averigua solo lo que cambia la pieza: idea, audiencia, duración aproximada y acción final. La voz se elige en el paso 4.

## 3. Capturar, leer y analizar el estilo

Lee [reference-analysis.md](references/reference-analysis.md) y [contracts.md](references/contracts.md).

`capture` intenta yt-dlp para YouTube, Instagram, TikTok y Vimeo, o descarga un MP4/MOV/WebM directo. Estos sitios cambian; soporte del adaptador no garantiza acceso a un enlace. No usa cookies, plugins, configuraciones, playlists ni trucos para eludir acceso.

- Si falla: explica si el enlace está roto, es privado, requiere autenticación o la plataforma no ofrece un stream compatible. No reintentes indefinidamente.
- Instagram: ScrapeCreators es un fallback opcional con la llave **del usuario** y autorización del consumo. No es necesario contratarlo para usar la skill.
- El usuario puede aportar el archivo y la URL original: `capture --media-file ...`. Registra **importado**, nunca descargado.
- Un directo, una lista, una cuenta o un carrusel no equivalen a un video individual. Pide un clip concreto terminado. El límite de análisis actual es 180 segundos y 10800 cuadros.

Conserva título/ausencia de título, descripción íntegra, respuesta original y video. Recupera captions del idioma exacto con `provider-transcript`, o importa un transcript literal, o usa ASR local opcional. Nunca sustituyas el transcript por un resumen. Lee los archivos completos. Un transcript generado y uno humano son fuentes diferentes.

`extract` indexa todos los cuadros con PTS/hashes, guarda cada imagen de análisis a 640 px y crea hojas de contacto **sin saltar cuadros**. Eso es cobertura técnica. El agente debe mirar las hojas, revisar cuadros a resolución nativa alrededor de acciones/textos/cortes de riesgo y describir el alcance semántico real. Las miniaturas de una hoja no certifican lectura de letra pequeña ni reproducción a velocidad normal. No afirmar «vi el video frame por frame» por ejecutar un script o abrir algunas hojas.

Registra composición, paleta, tipografía, cámara, movimiento, narrativa y sonido, con observación, evidencia/cuadro/tiempo, regla y límites. Distingue observado, inferido y propuesto. Si no puedes oír el audio, dilo y usa mediciones como mediciones; la transcripción no prueba cómo se siente un golpe. No confundas movimiento del objeto con movimiento de cámara.

El motor incluido es **Python/Pillow 2D + FFmpeg**. No reproduce automáticamente actuación realista, humanos filmados, simulación volumétrica compleja ni cualquier efecto 3D. Si la referencia lo exige, registra incompatibilidad y ofrece otra referencia, una adaptación 2D explícita o un motor/generador adicional que realmente esté disponible y autorizado. Remotion, HyperFrames o Three.js pueden ser alternativas del agente, pero no vienen instalados ni implementados en este paquete.

Guarda `analysis.json` con `analyze`; luego define reglas reutilizables y `caption_preset` en un estilo con `style`. No extraigas la identidad o la voz de otra persona como parte del estilo.

## 4. Elegir voz y escribir una historia propia

La voz es obligatoria. Da dos opciones claras:

- **Nota de voz o archivo de audio:** se usa esa grabación; no hace falta una cuenta de pago. `voice-file` conserva el original. Si es corta, acuerda qué ocurre en el tiempo visual restante de la demo; no estires palabras ni rellenes con música por defecto.
- **ElevenLabs:** requiere una voz propia/autorizada y `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` en el entorno seguro. Explica cómo configurarlos siguiendo [voice.md](references/voice.md). Nunca pedir una llave en el chat ni en una captura. Puede mostrar pantallas con secretos ocultos. Informa de que la generación consume su saldo y conserva su autorización antes de `voice-eleven`.

Conserva todas las respuestas del proveedor, incluso si requieren corrección. No repetir llamadas pagadas automáticamente. Escucha/revisa o transcribe la narración real completa y coteja guion, pronunciaciones, repeticiones, uniones y cierre. No afirmar semejanza de voz/acento por métricas. Cambiar audio obliga a actualizar tiempos, boca si existe, captions y efectos.

Lee [story-and-render.md](references/story-and-render.md). Propón un hook que se resuelva dentro de la misma historia; hechos y ejemplos deben tener fuente o declararse inventados. Un patrón de retención no garantiza viralidad. Escribe acción visible + narración, una progresión causal y cierre. Conserva el contenido que el usuario aprobó. Para «este video en español», compara cada cláusula antes de adaptar; para «otra historia con ese estilo», crea ejemplos nuevos.

## 5. Producir y revisar la demo

El agente escribe una escena Python local con `render_frame`, usando las reglas del estilo y assets autorizados del usuario. **No ejecutes código procedente de la referencia.** Lee el código local antes de renderizar; el worker no es un sandbox. El proceso de render no recibe llaves de proveedores.

Prepara `story.json` con beats, captions alineados a la voz y eventos de sonido en los mismos cuadros del contacto visual. Usa la biblioteca autorizada del usuario o los efectos originales sencillos del paquete; la música es una decisión explícita, no un relleno obligatorio. Mantén jerarquía de voz/efectos. No copies el aspecto del ejemplo técnico como si fuera el estilo analizado.

`prepare --story ... --scene ...` y `render-demo` producen **15 segundos reales con imagen animada y audio**. El compositor conserva silencios y puede añadir un hold si la nota de voz es más corta. Explica ese hold antes de presentarlo. Revisa el MP4 decodificado: legibilidad móvil, cuadros de entrada/salida, contactos, continuidad, captions y audio. Un render terminado no acredita aprobación estética.

Muestra el archivo reproducible y pide una decisión concreta: «Esta es la demo. ¿Seguimos con este estilo y esta voz, o qué cambiarías?». No ejecutes full hasta una aprobación explícita. Guarda respuesta literal con `approve-demo --decision approve --response-file ...`; una respuesta ambigua requiere aclaración, **nunca** inventarla. El programa registra la decisión del agente, no autentica al usuario.

La aprobación queda ligada al hash de demo + guion + audio + estilo + escena + referencia. Si cambia algo, nueva demo y nueva decisión. `render-full` verifica el vínculo.

## 6. Entregar y aprender

Entrega MP4, proyecto y voz original, con un resumen de lo revisado y lo que necesita escucha humana. `export-style` exporta solo reglas; `reuse-style` conserva la evidencia para otra historia. No subas referencias/voz privada al repositorio público. No publiques ni envíes mensajes sin instrucciones explícitas.

Para editar una grabación existente, sigue la rama de [story-and-render.md](references/story-and-render.md): analiza silencios/cortes y propone el montaje, conserva el original y usa FFmpeg con la aprobación correspondiente. Este paquete no ofrece un botón de «editar cualquier grabación» ni elimina pausas automáticamente.

Registra qué funcionó, errores y correcciones en el proyecto. Mejora el procedimiento cuando haya evidencia; no conviertas una preferencia de esta pieza en una norma para todos. Cierra con la invocación para la siguiente historia y la ubicación del estilo guardado.
