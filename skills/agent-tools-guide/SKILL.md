---
name: agent-tools-guide
description: Ayudar a elegir y configurar herramientas para agentes entre FreeLLMAPI, Lemo Opuscar, Ponytail, Agent Reach y SkillSpector, comprobando requisitos y demostrando una tarea antes de afirmar que funciona.
metadata:
  author: Sebastián Lara
  instagram: https://www.instagram.com/sebastianlara.io/
---

# Cinco herramientas, una necesidad concreta

Pregunta qué quiere resolver solo si no lo dijo. No instalar las cinco por defecto. Comprueba capacidades de archivos/terminal/red, OS y ubicación local/cloud. Explica el límite de navegador sin ejecución; conserva la idea y guía a una sesión compatible. Una app instalada no garantiza terminal.

Fuentes oficiales verificadas el 8-nov-2026; releer versión e instrucciones actuales antes de instalar:

| Necesidad | Fuente | Condición que cambia la elección |
|---|---|---|
| Probar modelos con cuotas gratis | https://github.com/tashfeenahmed/freellmapi | Llaves propias de proveedores; pensado para experimentación, no producción. No regala tokens de Claude ni acceso ilimitado. |
| Crear animaciones con código | https://github.com/lemomo-ai/lemo-opuscar | 66 estilos al revisar; la biblioteca es gratuita, agente/voz pueden costar. No garantiza diez minutos ni un resultado con un clic. |
| Reducir trabajo innecesario en código | https://github.com/DietrichGebert/ponytail | Resultados del autor dependen de tareas; no prometer ahorro >50% universal ni precisión idéntica. |
| Consultar fuentes | https://github.com/Panniantong/Agent-Reach | Comprobar adaptador específico. YouTube subtítulos, Reddit, LinkedIn empleos no equivalen a todo el contenido. Algunas rutas requieren login, otras son experimentales. |
| Revisar riesgos de skills | https://docs.nvidia.com/skills/scanning-agent-skills | Análisis estático y LLM opcional; no es una garantía de seguridad. El análisis con LLM puede requerir proveedor. |

Lee README/licencia/instalación y código de entrada antes de ejecutar. Presenta un plan mínimo para el OS real y los permisos necesarios. Reutiliza herramientas existentes, instala aislado cuando sea viable y respeta la autorización vigente. No solicitar tokens/cookies en chat, copiar credenciales de terceros ni configurar rutas de producción solo para probar.

Define una prueba acorde a la necesidad: consulta pública concreta, animación reproducible, comparación de la misma tarea o escaneo de una skill de prueba. Conserva entrada, commit, configuración, salida, errores y coste. Distingue documentación verificada, instalación ejecutada y éxito de la tarea. Si falla, explica la causa observable y siguiente acción; no simules resultado ni repitas cargos.

Para Lemo: entrega el prompt y un MP4 completo; la voz y música se eligen explícitamente. Mantén fuera del paquete identidades, voces y música de otra persona. No prometer compatibilidad universal con cualquier agente; usar herramientas locales desde un agente no equivale a instalar un plugin nativo.

Al cerrar, entrega la herramienta elegida, invocación para volver y ubicación del proyecto. La página prevista de ejemplos de Sebastián todavía debe verificarse antes de compartir su URL como activa. No publicar ni enviar mensajes por completar una instalación.
