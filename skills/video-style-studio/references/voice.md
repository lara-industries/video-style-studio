# Voz sin secretos en chat

La opción de menor fricción es una nota de voz o archivo: el agente la importa con `voice-file`. Se conserva el original, convierte formato a PCM estéreo 48 kHz y mide nivel. Aplica solo ganancia conservadora (máximo +12 dB, techo de pico −2 dBFS), nunca eco, clonación, cambio de tono o velocidad. Si sigue demasiado baja, se guarda y se pide una grabación más próxima al micrófono antes de mezclar efectos.

Una nota más corta de 15 s se puede usar: queda un cierre visual explícito hasta completar la demo. El agente acuerda ese hold o propone ampliar la narración, sin estirar palabras. El demo se escucha antes de aprobar el video completo.

## ElevenLabs opcional

El usuario usa su propia cuenta/saldo y una voz que tiene derecho a usar. Puede ser su clon autorizado o una voz disponible para él. La skill no crea un clon ni hereda una voz de su autor.

1. Mostrar el texto exacto y explicar que la generación consume el saldo del usuario.
2. Registrar autorización `consent --scope elevenlabs-generation --decision approve --response-file ...`.
3. Configurar `ELEVENLABS_API_KEY` y `ELEVENLABS_VOICE_ID` mediante el gestor de secretos del agente/sistema. No guardarlos en el proyecto, argumentos del comando, un `.env` público ni logs. No pedir capturas que muestren llaves. Voice ID no sustituye autorización de uso.
4. Ejecutar `voice-eleven --workspace ... --text-file narration.txt`. La configuración por defecto usa `eleven_multilingual_v2`; comprobar compatibilidad de la voz/modelo antes de proponer otro. No prometer todos los modelos.
5. Conservar la respuesta original **antes** de validación/conversión. No repetir cargos automáticamente si algo falla. Cotejar el archivo de audio real completo, no solo la entrada de texto del modelo.

Si el usuario prefiere escribir la llave en una terminal local visible, el helper `scripts/voice_with_secret.py` usa entrada oculta y variables solo en ese proceso. No usarlo en una herramienta de terminal que mande las teclas del usuario al chat. La opción del gestor de secretos es preferible. Ejemplo de llamada (sin llave en argumentos):

```sh
python scripts/voice_with_secret.py --workspace /ruta/proyecto --text-file /ruta/narration.txt
```

Verificar palabras difíciles, silencios entre frases, uniones y final. Una transcripción exacta prueba contenido, no semejanza ni naturalidad. Si la voz cambia, repetir reloj/captions/sonido/demo. El usuario puede enviar pantallas de configuración con los campos secretos ocultos para recibir ayuda; nunca solicitar la llave visible.
