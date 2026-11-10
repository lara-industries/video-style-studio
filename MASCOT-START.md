# Tu primera mascota animada

Una idea, un personaje propio y tu voz. Tu agente te acompaña hasta una demo de quince segundos que puedas ver y corregir.

Abre Claude Code, Codex u otro agente con archivos, terminal y visión en tu computador. Pega esto:

```text
Lee https://github.com/lara-industries/video-style-studio/blob/main/MASCOT-START.md y guíame para crear mi propio personaje animado y una primera demo de 15 segundos con mascot-video-guide. Comprueba mis herramientas, explícame lo que falte y acompáñame paso a paso.
```

No necesitas llegar con todo instalado. El agente empieza revisando tu equipo. Te pedirá una referencia, una idea y tu voz; puede ayudarte a preparar cada una.

## Lo que vamos a hacer

1. **Preparar el taller.** Comprobar tu equipo y explicarte qué falta antes de instalar.
2. **Elegir el rumbo.** Estudiar una referencia accesible y decidir qué quieres contar.
3. **Crear tu personaje.** Una identidad neutral, las expresiones necesarias y archivos con fondo transparente.
4. **Escribir la historia.** Un guion corto que tu personaje pueda explicar con intención.
5. **Preparar la voz.** Tu grabación o una voz autorizada con un proveedor como ElevenLabs.
6. **Verlo en movimiento.** Una demo de quince segundos; el video completo espera tu aprobación.

La skill y el motor local son gratuitos. Tu agente y los proveedores de imagen o voz pueden tener coste. Si no tienes un generador conectado, puedes crear las imágenes en Gemini o ChatGPT e importarlas. No incluye la voz, el avatar ni el estilo privado de Sebastián.

## Para el agente

Descarga el repositorio completo y lee `skills/mascot-video-guide/SKILL.md`. Comprueba tus capacidades reales y dónde se ejecuta la sesión; una app de escritorio no demuestra acceso al computador y un contenedor cloud no es el disco del usuario. Si no tienes ejecución local, explica el límite y ayuda a usar una sesión compatible. No afirmes que instalaste o renderizaste lo que no puedes comprobar.

Explica el recorrido, muestra un paso a la vez y conserva el avance. No asumas que existen Python, un proveedor de imágenes, una voz ni una clave de API. Presenta faltantes, destino, permisos y costes antes de instalar. Las claves se configuran por el mecanismo privado de cada proveedor, nunca pegadas en el chat.

Desde el checkout íntegro, `python scripts/install-mascot.py --destination RUTA_DE_SKILLS` copia la guía y el motor juntos después de la autorización pertinente. Conserva cualquier instalación previa y no instala dependencias. Si la ruta de instalación del agente requiere otra estructura, explícalo y preserva ambas carpetas completas y sus referencias relativas.

Verifica el motor con `skills/video-style-studio/scripts/studio.py doctor` usando el Python compatible. Lee sus referencias para instalación por sistema, captura y contrato de escenas. El motor incluido usa Python/Pillow y FFmpeg; la actuación y las escenas las construye el agente con los assets aprobados. No promete animación automática perfecta ni sincronización labial lista para cualquier personaje.

Muestra la identidad neutral, escucha la voz y prepara una locución de piloto que cierre una frase antes de los quince segundos. Revisa el MP4 real: legibilidad, movimiento, transparencia, continuidad y sonido. Distingue pruebas técnicas de revisión creativa y aprobación humana. No avances al completo sin la aprobación exacta de la demo.

## La próxima vez

```text
Usa mascot-video-guide con mi personaje guardado. Quiero que explique esta idea: [idea]. Muéstrame primero una demo de quince segundos.
```

Creado por [Sebastián Lara · @sebastianlara.io](https://www.instagram.com/sebastianlara.io/).
