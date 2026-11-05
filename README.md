# Video Style Studio

Una skill para crear videos animados con tu agente, una referencia y tu propia idea.

Le das un enlace, le cuentas qué te gusta y aportas la voz. Tu agente estudia el estilo, prepara una historia nueva y te muestra una prueba de 15 segundos. El video completo llega después de que apruebes esa prueba.

**[Empezar paso a paso](START-HERE.md)** · [La skill](skills/video-style-studio/SKILL.md) · [Licencia MIT](LICENSE)

## Pega esto en tu agente

```text
Lee https://github.com/lara-industries/video-style-studio/blob/main/START-HERE.md
y ayúdame a instalar video-style-studio. Primero comprueba que puedes trabajar
en mi computador y explícame qué vas a instalar. Guíame paso a paso.
Quiero crear un video animado: pídeme una referencia y mi idea, y ayúdame a
elegir entre una nota de voz o ElevenLabs. Muéstrame primero una prueba de
15 segundos y espera mi aprobación antes de hacer el video completo.
```

Usa un agente con archivos, ejecución local y capacidad de ver imágenes: por ejemplo Claude Code en modo Local o ChatGPT/Codex con trabajo local habilitado. Un chat en el navegador no instala herramientas en tu computador. Si tu sesión no tiene esas capacidades, la skill debe explicártelo y ayudarte a abrir una compatible.

## Qué sucede

1. **Preparar tu computador.** El agente comprueba el sistema y te muestra qué falta, para qué sirve y qué permiso necesita. Conserva tus archivos y espera tu autorización antes de instalar software.
2. **Estudiar una referencia.** Descarga el enlace cuando es accesible, conserva descripción y transcripción, extrae los cuadros y estudia composición, movimiento, letra, narrativa y sonido. Un enlace cerrado o una técnica incompatible se resuelven antes de producir.
3. **Guardar tu estilo.** El resultado es una ficha reutilizable. La referencia orienta el lenguaje visual; la historia y los materiales del nuevo video se crean para tu idea.
4. **Añadir tu voz.** Puedes aportar una nota de voz o usar ElevenLabs con una voz propia o autorizada. La suscripción de tu agente no incluye los créditos de ElevenLabs.
5. **Ver una prueba.** Recibes un MP4 de 15 segundos con audio. Puedes pedir cambios con tus palabras.
6. **Completar y revisar.** Tras tu aprobación, el agente produce el video completo, revisa el export y te entrega los archivos. Cambiar el guion, el estilo o la voz invalida la aprobación anterior cuando afecta al resultado.

## Qué puede hacer esta versión

El motor incluido produce animación 2D con Python/Pillow y FFmpeg. El agente escribe la escena a partir de la ficha de estilo. No es un catálogo de plantillas ni un modelo de generación de video. La calidad visual depende del análisis y de la escena que construya el agente; los controles técnicos no pueden aprobar tu gusto por ti.

Referencias de imagen real, actuación humana realista, simulación 3D compleja o efectos que exijan otro motor necesitan una adaptación acordada u otras herramientas. La skill debe explicarlo antes de prometer el resultado. Remotion y HyperFrames son posibles extensiones del flujo; no se instalan ni se presentan como renderers implementados de este paquete.

La descarga de plataformas depende de que el enlace sea accesible y del extractor disponible. Si falla, puedes aportar el video descargado por ti y conservar su URL como procedencia. Una importación no se registra como descarga automática.

## Compatibilidad y requisitos

- Python 3.10 o superior, FFmpeg/ffprobe y Pillow para el motor incluido.
- yt-dlp para la ruta de descarga de plataformas; Whisper es opcional para transcripción local.
- macOS, Windows y Linux: el agente detecta el sistema y propone la instalación correspondiente. La disponibilidad de una aplicación de agente es independiente de que el código sea portable.
- La skill usa el formato abierto [Agent Skills](https://agentskills.io/specification). Se instala en la carpeta de skills que admita el agente o se carga manualmente mediante su `SKILL.md`.

No necesitas una clave de OpenAI para usar el motor local. Tu agente puede requerir su propia suscripción. ElevenLabs y ScrapeCreators son servicios opcionales: el agente explica sus costes antes de usarlos y recibe las credenciales desde un entorno privado, nunca desde una captura o un mensaje público.

## Para quienes quieren inspeccionar el código

```sh
python skills/video-style-studio/scripts/studio.py doctor
python skills/video-style-studio/scripts/studio.py --help
```

`doctor` hace comprobaciones locales; no instala software ni acredita por sí solo que el chat esté ejecutándose en la app del usuario. El historial del proyecto distingue descarga, extracción de cuadros, revisión del agente, aprobación del usuario y exportación.

La escena es código Python que se ejecuta localmente. El agente debe leerla antes de ejecutarla. Este paquete no es un sandbox de código.

## Pruebas y licencias

El [CI público](https://github.com/lara-industries/video-style-studio/actions/workflows/ci.yml) ejecuta pruebas unitarias y una integración con instalación, demo de 15 segundos, aprobación y export completo en macOS, Windows y Linux. La integración usa una referencia y audio sintéticos; valida el funcionamiento, no la calidad creativa de una referencia ni el parecido de una voz.

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/integration.py --output /ruta/vacia/prueba
```

El código usa licencia MIT. La fuente incluida para captions es Noto Sans, con [su licencia SIL OFL](skills/video-style-studio/assets/fonts/OFL.txt).

## Volver a usarla

```text
Usa la skill video-style-studio y crea un video animado con mi estilo
<nombre del estilo> sobre <idea>. Usa esta narración: <archivo de audio>.
```

Si aún no guardaste un estilo, el agente te pedirá una referencia y empezará por estudiarla. Los archivos de trabajo, la voz y las referencias se guardan en tu proyecto local; no deben subirse a este repositorio.

Creado por [Sebastián Lara](https://www.instagram.com/sebastianlara.io/).
