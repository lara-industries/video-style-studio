# Capacidades, no promesas por marca

El formato de skill es texto portable. Su ejecución exige herramientas reales. Un agente debe poder leer/escribir archivos del usuario, ejecutar procesos locales, ver las imágenes y devolver el MP4. Una integración de voz/ASR puede ser local o conectada. La inspección perceptual de audio no se presupone.

| Entorno | Cómo decidir |
|---|---|
| Claude Code local / escritorio con trabajo local | Ejecutar doctor, verificar directorio accesible y evidencia de ubicación local. |
| Codex local / escritorio con ejecución local | Mismo control; consultar directorio de skills de esa versión. |
| ChatGPT con Work locally habilitado | Puede servir si la sesión ofrece archivos/ejecución en el computador; comprobar capacidades. |
| Chat web estándar sin terminal/archivos | Preparación de idea posible; instalación, descarga y render no se afirman. |
| Shell en nube/contenedor remoto | Puede ejecutar código, pero no es la app/computador del usuario. Esta edición pide pasar a un entorno local para producir; conservar el brief. |
| Linux sin app gráfica compatible | Agente CLI local con herramientas y capacidad visual, o un handoff explícito de imágenes a un agente que las vea. |

`doctor` siempre devuelve ubicación/app `unknown`: saber que Python puede escribir no prueba que se esté en el escritorio de la persona. `confirm-environment` registra evidencia del runtime o la confirmación explícita del usuario y etiqueta su origen. Nunca infiere identidad de la app mirando procesos.

Fuentes oficiales para revisar compatibilidad cuando cambie: [ChatGPT Work locally y skills](https://learn.chatgpt.com/docs/use-chatgpt), [Build skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code Desktop](https://code.claude.com/docs/en/desktop), [Agent Skills specification](https://agentskills.io/specification). Son capacidades condicionadas a versión, permisos y producto; no son pruebas de esta sesión.

Esta edición implementa Pillow 2D + FFmpeg. No instala Remotion, HyperFrames, Three.js ni generadores de imagen/video. Un agente puede proponerlos si una referencia los requiere, explicando instalación, costes y una prueba adicional. No marcar compatible un video realista porque se pueda dibujar un cuadro parecido.
