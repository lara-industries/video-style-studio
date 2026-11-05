# Narrativa y producción

Construye la historia desde la idea que debe quedar, la evidencia y la acción que se espera. Una frase vistosa sin relación con el resto no es un hook útil.

Para una pieza nueva, compara dos o tres mecanismos de inicio si el usuario todavía no eligió uno: acción interrumpida, consecuencia inesperada o situación reconocible que cambia. Escribe primera imagen, frase, sonido y promesa; señala dónde se resuelve. La alternativa cambia el mecanismo, no solo un adjetivo. Elige por claridad móvil, especificidad, coherencia y capacidad real de producirla; no prometas viralidad.

Dibuja un mapa causal: qué sabe el espectador, qué cambia, qué acción visible provoca el siguiente beat y qué queda abierto. Quita repeticiones que no aportan información. No inventes experiencias o autoridad del usuario. Marca en el expediente hechos, metáforas, adaptaciones y ficción sin meter rótulos técnicos en pantalla por defecto.

Para una adaptación del video de referencia, compara todas las cláusulas y conserva orden/ejemplos prometidos salvo cambio explícito del usuario. Para inspiración estilística, crea contenido nuevo. La fuente literal siempre permanece aparte.

## Dirección y físicas

Traducir reglas a acciones verificables: una pieza cae por una trayectoria acelerada, toca un soporte, lo deforma, rebota y se asienta. El movimiento de cámara revela información espacial; no se sustituye por una sucesión de fundidos si la referencia tiene continuidad. Las salidas importan tanto como las entradas. La deformación y el trail responden a velocidad, no a un seno constante.

Coloca voz, captions, aparición de UI y contactos sonoros en un reloj. Los efectos siguen la colisión visible, no una palabra aproximada. Una boca usa voz/timing real y se cierra en pausas; si no se implementó rig, no afirmar lip sync. No todos los estilos necesitan personaje o subtítulos de la misma forma.

La tipografía debe ser legible y tener licencia adecuada. El compositor base usa la fuente incluida con Pillow; una fuente del usuario requiere comprobar origen y guardarla como asset autorizado. Para una tipografía específica, implementa la escena/preset correspondiente y compruébala; no declarar fidelidad pixel perfect por elegir una fuente parecida.

## Revisión del archivo real

1. Esperar a que el proceso termine y validar export; un archivo que crece no está listo.
2. Decodificar inicio, entradas, contactos, salidas, todas las líneas de captions y cierre. Mirar las secuencias de riesgo, no solo un collage bonito.
3. Revisar/escuchar voz e impactos si la herramienta lo permite. Medidores y ASR solo prueban sus respectivas propiedades.
4. Comparar con la referencia: qué reglas se aplicaron, qué es adaptación propuesta y qué no se pudo verificar.
5. Mostrar el MP4 de 15 s. El usuario aprueba el resultado concreto, no un plan. No rellenar una aprobación para que el gate pase.

Guardar guion limpio, escena, tiempos, audio original/procesado, eventos, parámetros y evaluación. La aprobación de una demo no autoriza publicar el completo.

## Rama de grabación existente

Si la persona quiere editar una grabación, conservarla y estudiar transcript, silencios reales y cortes. El agente puede construir un montaje FFmpeg con una lista explícita de segmentos, captions y audio autorizado, o usar el editor/motor disponible. Un detector de silencio no sabe qué pausa es dramática: presentar criterio y una prueba antes de eliminar pausas en todo el archivo.

Esta edición entrega helpers de análisis de referencia, voz y composición 2D. **No implementa edición automática de grabaciones, B-roll, diarización ni recorte inteligente.** No presentar esas tareas como un botón existente. Si se programa esa rama para el usuario, conservar proyecto, realizar demo equivalente y validar export/audio antes de una producción completa.
