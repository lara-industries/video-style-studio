# Instalación consentida y comprobable

El agente opera estos comandos. Primero presenta el plan en lenguaje sencillo y obtiene autorización para instalar terceros. Guarda la respuesta con `consent --scope third-party-install`. No convierte un error de permisos en autorización para elevar privilegios. Si el usuario ya autorizó el mismo plan, no vuelve a preguntarlo.

La carpeta de esta skill es autocontenida. Ejecutar `python scripts/studio.py doctor` desde ella. Python 3.10+; entorno recomendado 3.11. El compositor requiere Pillow, FFmpeg y ffprobe con encoder libx264. yt-dlp es opcional si el usuario importa sus videos; Whisper es opcional si hay captions/transcript.

## macOS

Si faltan Python o FFmpeg y Homebrew ya existe, proponer:

```sh
brew install python@3.11 ffmpeg
python3.11 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/studio.py doctor
```

Si Homebrew no existe, explicar que sería otro gestor de paquetes y ofrecer instalarlo desde [su sitio oficial](https://brew.sh) con autorización separada, o usar el instalador oficial de Python y un FFmpeg ya disponible. No ejecutar un `curl | sh` silencioso. No reemplazar el Python del sistema.

## Windows (PowerShell)

Si faltan herramientas y Winget está disponible, proponer:

```powershell
winget install --id Python.Python.3.11 --exact
winget install --id Gyan.FFmpeg --exact
```

Abrir una terminal nueva para refrescar PATH y continuar desde la carpeta de la skill:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts\requirements.txt
.\.venv\Scripts\python.exe scripts\studio.py doctor
```

No requiere activar un script de PowerShell ni cambiar ExecutionPolicy. Si Winget no está disponible, usar el instalador oficial de Python y un build de FFmpeg enlazado desde [ffmpeg.org/download.html](https://ffmpeg.org/download.html); comprobar PATH y encoder. No solicitar que desactive antivirus.

## Linux

Ubuntu/Debian, tras autorización:

```sh
sudo apt-get update
sudo apt-get install python3 python3-venv ffmpeg
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/studio.py doctor
```

Python debe ser3.10+. Para otras distribuciones, usar su gestor y comprobar las mismas capacidades; estos comandos apt no son universales. El agente CLI local es alternativa si no hay app gráfica compatible.

## Instalar la skill en el agente

Usar el Python disponible y la ruta completa al archivo `scripts/studio.py`. Este comando **solo copia la skill**; no instala terceros ni modifica perfiles de shell.

```sh
python scripts/studio.py install --destination /ruta/del/proyecto/.agents/skills
```

- Codex / runtimes que descubren Agent Skills: `.agents/skills` del proyecto o directorio de usuario documentado por el runtime. Confirmar dónde busca skills la versión instalada.
- Claude Code: `.claude/skills` del proyecto o del usuario, según su configuración actual.
- Otros agentes: `.skills` u otra carpeta que su documentación admita. Copiar allí no demuestra descubrimiento; abrir `video-style-studio/SKILL.md` explícitamente y verificar una invocación.
- ChatGPT: usar un entorno con trabajo local, acceso a estos archivos y ejecución habilitados; cargar la carpeta por el mecanismo de skills que esa versión ofrezca. No prometer que pegar el nombre en cualquier chat instala herramientas.

Ejemplos, desde el checkout del paquete:

```sh
python skills/video-style-studio/scripts/studio.py install --destination .agents/skills
python skills/video-style-studio/scripts/studio.py install --destination .claude/skills
python skills/video-style-studio/scripts/studio.py install --destination .skills
```

Elegir **un** destino apropiado, no instalar los tres por costumbre. Si ya existe, el instalador se niega a sobrescribir. Revisar la versión y conservar la anterior antes de actualizar. Tras instalar, pedir: «Usa video-style-studio y comprueba que puedes trabajar en mi computador». La prueba real de acceso manda.

## ASR opcional

Si no hay transcript, presentar tamaño/coste de descarga y pedir autorización antes de instalar un motor/modelo local:

```sh
python -m pip install -r scripts/requirements-asr.txt
```

`transcribe --model-path /ruta/a/modelo-faster-whisper` solo acepta un modelo local y no descarga uno a escondidas. El agente puede usar otro ASR ya conectado, conservar su salida completa y registrarla con `transcript --source agent-ASR-generated`. No inventar transcript si no hay capacidad. La voz del video de referencia y la narración nueva son archivos distintos.
