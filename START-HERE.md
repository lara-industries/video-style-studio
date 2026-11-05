# Empieza aquí

No necesitas saber programar. Tu agente ejecuta el trabajo y tú eliges la referencia, aportas la voz y apruebas el resultado.

## Antes de empezar

Abre la aplicación de escritorio de tu agente y una sesión que trabaje en tu computador. En Claude usa Claude Code y el entorno Local. En ChatGPT usa el trabajo local de ChatGPT/Codex, si está habilitado para tu cuenta. Una sesión cloud dentro de una app de escritorio sigue siendo cloud.

Si estás en Linux y tu aplicación no está disponible, el agente debe explicarte la alternativa local compatible, como su CLI, antes de continuar. No debe decir que detectó una app solo porque encontró un proceso abierto.

Ten a mano:

- Un enlace a un video de referencia accesible.
- La idea que quieres contar y qué te gusta de la referencia.
- Una nota de voz con la narración, o una cuenta de ElevenLabs con tu voz.

Puedes resolver la voz durante la preparación. No pegues claves de API en el chat ni las muestres en capturas.

## Instrucciones para el agente que está leyendo esta página

Ayuda a la persona a completar el flujo, no le entregues una lista larga de comandos para que se las arregle sola. Mantén visibles el paso actual, lo que acabas de comprobar y la única decisión que necesita tomar a continuación.

1. **Comprueba dónde puedes trabajar.** Identifica tus capacidades reales de archivos, procesos y visión. Si puedes ejecutar comandos locales, descarga este repositorio a una carpeta nueva y revisa su contenido antes de ejecutarlo. No confundas una VM del navegador con el computador de la persona. Si la ubicación no puede verificarse, dilo y pregunta dónde abrió la sesión; ofrece instrucciones concretas para cambiar al modo local. Una confirmación del usuario se registra como tal, no como detección automática.
2. **Lee la skill.** Abre `skills/video-style-studio/SKILL.md`. Sus referencias describen instalación, captura, voz y contrato de escenas. El formato del paquete es independiente del proveedor del agente, pero sus capacidades no lo son.
3. **Explica la instalación antes de hacerla.** Detecta sistema y herramientas existentes. Resume únicamente lo que falte: qué instalarás, qué ocupa/descarga cuando se conozca, dónde quedará y si pide permisos o un servicio de pago. Propón el plan y espera autorización. No ejecutes instaladores opacos, no sobrescribas una skill o proyecto ya existente y no guardes secretos en el repositorio.
4. **Instala y verifica.** Usa el procedimiento del sistema operativo descrito en la skill. Instala la carpeta completa, no solo el archivo `SKILL.md`, en la ubicación que admita el agente. Ejecuta `doctor` y resuelve los fallos reales. Una instalación parcial no se anuncia como terminada.
5. **Pide la referencia y la idea.** Si pidió un video sin tener un estilo guardado, explica que primero estudiarás la referencia. Descárgala cuando sea accesible y analiza los archivos reales. Conserva descripción y transcript literales. Lee las hojas de cuadros y vuelve a los cuadros nativos en texto pequeño, transiciones, contactos y movimientos rápidos. Distingue cobertura técnica de revisión visual. Si no puedes abrir o interpretar algo, informa el límite y propone una alternativa concreta.
6. **Elige la voz con la persona.** Una nota de voz evita tener que usar ElevenLabs. Si elige ElevenLabs, explícale cómo crear una clave limitada y encontrar el ID de su voz; guíala con capturas de ajustes con las claves ocultas si lo necesita. No clones una voz de la referencia ni uses una identidad sin autorización. Explica que el proveedor cobra por generación antes de hacerla.
7. **Define y muestra el demo.** Presenta una propuesta breve de historia y movimiento. Construye una escena nueva y renderiza una prueba de 15 segundos con audio. Abre o entrega el archivo real para que pueda verlo. Pide una opinión concreta sobre voz, estilo y ritmo.
8. **Espera la aprobación del demo.** No inventes respuestas afirmativas ni generes el completo porque pasaron unos minutos. Registra la respuesta y el archivo exacto elegido. Tras aprobar, termina el video y revisa el export. Si cambia una entrada relevante, revisa qué aprobación quedó obsoleta.
9. **Cierra con una forma fácil de volver.** Entrega el MP4, su carpeta y el nombre del estilo guardado. Explica qué frase puede usar la próxima vez. Publicar en redes o enviar a otras personas requiere su instrucción específica.

No completes el flujo escribiendo un JSON que diga que lo revisaste: haz las comprobaciones y conserva sus resultados. Los errores deben dejar los originales recuperables y una explicación útil, no un intento de repetir cargos o instalaciones a ciegas.

## La próxima vez

```text
Usa video-style-studio. Quiero un video con mi estilo <nombre>, sobre
<idea>. Aquí está mi narración: <archivo>. Primero muéstrame 15 segundos.
```

Si te gusta una referencia nueva, pídelo así:

```text
Usa video-style-studio. Estudia el estilo de <enlace> y dime qué podemos
reproducir con las herramientas disponibles. Quiero contar <idea> con mi
propia voz. Guárdalo como <nombre> y prepara una prueba de 15 segundos.
```
