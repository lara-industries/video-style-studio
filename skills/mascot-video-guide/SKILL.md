---
name: mascot-video-guide
description: Guiar desde cero la creación de un personaje propio con expresiones y una demo animada de 15 segundos, comprobando herramientas, imágenes y voz antes del montaje.
metadata:
  author: Sebastián Lara
  instagram: https://www.instagram.com/sebastianlara.io/
  repository: https://github.com/lara-industries/video-style-studio
---

# Tu personaje explica tus ideas

Esta guía coordina herramientas reales; no incluye un generador de imágenes ni la voz o personaje de Sebastián. La base de montaje es [Video Style Studio](../video-style-studio/SKILL.md), con Python/Pillow y FFmpeg. No afirma usar Remotion si no lo has instalado y usado como alternativa explícita.

Abre explicando el recorrido: preparar el equipo, elegir referencia e idea, crear personaje/expresiones, guion/voz, demo de quince segundos y revisión. Muestra el paso actual y una acción siguiente; no una lista de comandos para que la persona se las arregle sola.

## Preparar sin asumir

Desde el checkout completo, instala ambas carpetas con `python scripts/install-mascot.py --destination RUTA_DE_SKILLS` después de explicar el destino y obtener la autorización aplicable. El comando conserva cualquier instalación existente y no instala dependencias. Al leer esta skill instalada, comprueba que el hermano `../video-style-studio/SKILL.md` existe; si falta, recupera el paquete completo desde el repositorio del metadata y repara esa dependencia antes de continuar. Estas instrucciones son autocontenidas: no dependen de un START-HERE fuera de la carpeta instalada. Comprueba archivos/terminal locales y OS; `../video-style-studio/scripts/studio.py doctor` informa sobre ese runtime, no sobre la app o computador del usuario. Si estás en navegador sin herramientas, avisa y ayuda a pasar a una sesión local compatible. Una app instalada no demuestra acceso al disco. Presenta instalación/coste/directorio y usa la autorización explícita vigente antes de instalar dependencias.

## Referencia y personaje

Pide URL de video accesible, idea, foto propia o descripción del personaje. Captura y estudia la referencia con Video Style Studio, conservando transcript y metadatos. Un estilo realista incompatible no se promete como animación 2D.

Descubre si hay proveedor de imágenes conectado con edición por referencia. Si no: ofrece conectarlo con instrucciones para ese proveedor o genera un prompt copiable para Gemini/ChatGPT y ayuda a importar los resultados. No pedir claves en mensajes/capturas. No hace falta comprar otro servicio si puede generar e importar imágenes.

Crea primero el personaje neutral y pide revisar su identidad. Usa el mismo ancla para una hoja de expresiones. [Dirección y revisión](references/character-and-emotion.md) define estados y relación con voz; la hoja es para revisar, los sprites para montar. Revisa transparencia real, bordes, proporciones, tamaño y encuadre. Si tienes una hoja, divide por celdas verificadas, sin cortar pelo u orejas; no declares recorte perfecto sin abrir los archivos.

## Guion y voz

Escribe una explicación breve propia. Elige estados según lo que significa cada frase; no aleatorios para estimular. Aporta grabación propia o configura un proveedor con una voz autorizada. Conserva frases completas y el mismo contexto; no unir palabras sueltas ni cortar por huecos de alineación. Revisa voz antes de animar. Con TTS el estilo vocal puede requerir otra toma; no se garantiza emoción por una etiqueta.

## Demo real

Usa el contrato de escenas de Video Style Studio y crea la escena con sprites propios. Liga emoción visual a intervalos de frase del audio real, con entrada/salida intencionales. Para hablar añade estados de boca coherentes, no solo saltos entre retratos. Si ese rig todavía no existe, muestra la limitación en el piloto antes de prometer lipsync.

Antes de renderizar, prepara una locución de piloto que termine una frase completa antes de quince segundos. Si dura menos, completa con un hold visual y silencio explicado; no cortes una narración larga exactamente en el segundo quince ni aceleres palabras para encajar. Renderiza quince segundos; revisa el MP4 y muestra resultado. No avances al completo sin aprobación exacta. Entrega proyecto/audio/assets y cómo retomar: «Usa mascot-video-guide con mi personaje guardado y cuenta esta idea…». No publicar, enviar mensajes ni subir retratos privados a GitHub.
