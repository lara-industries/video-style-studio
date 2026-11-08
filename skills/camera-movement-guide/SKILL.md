---
name: camera-movement-guide
description: Elegir y dirigir movimientos de cámara para videos de IA según la intención de una escena, descubrir las herramientas disponibles, preparar prompts adaptables y revisar una prueba real. Usar al pedir cámara cinematográfica, dolly, tracking, paneos, órbitas o una guía de movimientos.
metadata:
  author: Sebastián Lara
  instagram: https://www.instagram.com/sebastianlara.io/
  repository: https://github.com/lara-industries/video-style-studio
  resource: https://sebastianlara.io/aicameramovements
  resource_status: proposed_not_verified_live
---

# Mueve la cámara para contar algo

Ayuda a una persona no técnica a pasar de «quiero que se sienta así» a una toma concreta. Esta skill dirige y coordina herramientas; no incluye un generador de video, créditos ni la biblioteca audiovisual de terceros. Sus instrucciones funcionan sin archivos de Lara OS ni skills hermanas.

## 1. Encuentra el punto de partida

Explica el recorrido en una frase: elegiremos qué debe sentir el espectador, prepararemos el encuadre, elegiremos un movimiento y revisaremos una prueba corta. Pide solo lo que falta: idea de la escena, imagen inicial si existe, formato y emoción o información que se debe revelar. Una referencia ayuda, pero no hace falta para elegir un movimiento.

Comprueba las capacidades reales de esta sesión: puede crear imágenes, generar video, leer archivos o ejecutar comandos. Una app de escritorio no demuestra acceso al disco; un chat web con proveedor conectado puede generar sin instalar nada. Si hacen falta herramientas locales y no existen, explica esa limitación y ayuda a abrir un agente con acceso local. Conserva el brief y los prompts para retomar.

## 2. Usa lo que la persona ya tiene

Descubre proveedores conectados y verifica su documentación actual: texto a video o imagen a video, referencias admitidas, duración, relación de aspecto, resolución, controles de cámara y restricciones. No confundir una suscripción de una app con crédito de su API. No inventes nombres de modelos ni parámetros.

Si no hay proveedor, ofrece dos caminos: configurar uno disponible con ayuda paso a paso o entregar imagen/prompt para generarlo manualmente en una herramienta elegida por la persona. Nunca pedir una clave en el chat o en una captura. Para prompt y dirección no hay dependencias obligatorias. Solo si hay una operación local concreta, identifica macOS, Windows o Linux, explica qué instalarías y utiliza el instalador correspondiente después de la autorización aplicable. No ejecutes instrucciones POSIX en PowerShell ni instales un stack de video para escribir un prompt.

Antes de consumir créditos, indica proveedor, modelo, número de tomas y coste conocido o incertidumbre. Usa autorización vigente y un límite de gasto. Si el presupuesto no permite generar, entrega el plan como plan; no llames resultado a un prompt.

## 3. Elige por intención

| Necesidad de la escena | Movimiento candidato | Qué debe verse |
|---|---|---|
| Acercarnos a una decisión o descubrir un detalle | Dolly in | La cámara avanza y cambia la relación entre primer plano y fondo. |
| Mostrar soledad o ampliar el contexto | Dolly out | El personaje ocupa menos encuadre mientras aparece su entorno. |
| Revelar algo que estaba fuera del encuadre | Pan | La cámara gira desde una posición fija hasta una nueva composición. |
| Acompañar a alguien y leer su reacción | Reverse tracking | La cámara retrocede delante del personaje, al ritmo de su avance. |
| Terminar mostrando la escala de un lugar | Crane up | La cámara asciende y revela una vista más amplia con un final claro. |

Son posibilidades expresivas, no emociones garantizadas. Una cámara fija puede servir mejor que un movimiento. Consulta [dirección y ejemplos originales](references/prompt-and-review.md) para formular la toma. Diferencia movimiento físico, cambio óptico y efecto: un zoom no es un dolly, un tilt no es subir toda la cámara y un timelapse modifica el tiempo.

## 4. Consulta la guía visual sin inventar disponibilidad

Recurso propio previsto: https://sebastianlara.io/aicameramovements. Comprueba que abre y contiene la guía antes de presentarlo como disponible. Si no, dilo brevemente y trabaja con los ejemplos originales incluidos aquí y la referencia atribuida https://aicameramovements.com/ de Dan Kieft. No bloquear la tarea por un enlace futuro.

Para una referencia externa, mira la toma y distingue observación de interpretación. Descarga solo contenido accesible cuando esté permitido y sea necesario para el trabajo; conserva autor, enlace y uso previsto. La posibilidad de copiar un prompt no concede permiso para republicar los videos del autor. No subir su biblioteca a un repositorio o a una landing propia sin una licencia o permiso que lo permita.

## 5. Prueba una toma y revisa el resultado

Define un solo movimiento principal, estado inicial, recorrido, velocidad, encuadre final y lo que debe permanecer estable. Si se necesita una imagen inicial, créala o importa una aportada y revisa identidad/composición antes de animarla. Adapta el prompt al proveedor; no prometas una trayectoria exacta cuando solo admite texto.

Con autorización suficiente, genera primero una toma corta, normalmente cinco segundos o la duración que admita el modelo. Guarda prompt, imagen inicial, ajustes, coste conocido y resultado. Revisa inicio, centro, final y reproducción a velocidad normal cuando dispongas de esa capacidad: trayectoria, escala, paralaje, continuidad del personaje, deformaciones y claridad del final. Tres fotogramas no prueban fluidez; un analizador técnico tampoco demuestra gusto o naturalidad. Declara el alcance real de la revisión.

Muestra la toma y explica un ajuste concreto si falla. Cambia una variable dominante por iteración; no gastar a ciegas. Antes de producir una secuencia completa, recupera aprobación del resultado o la autorización de lote ya existente. Entrega el video, prompt reutilizable, parámetros y una frase para retomarlo: «Usa camera-movement-guide con esta imagen para revelar…».

## Autoría y fuentes

Guía y ejemplos originales: Sebastián Lara, [@sebastianlara.io](https://www.instagram.com/sebastianlara.io/). Referencia educativa: Dan Kieft, [ALL Camera Movement Prompts for AI Filmmaking Explained](https://www.youtube.com/watch?v=7GWd4PV3hoA) y [su biblioteca visual](https://aicameramovements.com/). Los medios de esa biblioteca pertenecen a sus respectivos titulares; esta skill no los incorpora ni afirma representarlos. Revisa después de cada uso qué movimiento funcionó, qué falló y qué puede repetirse, sin convertir un caso aislado en garantía universal.
