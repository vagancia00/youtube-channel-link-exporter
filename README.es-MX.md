<div align="center">
  <img src="assets/banner.svg" alt="YouTube Channel Link Exporter" width="100%">

  <p><strong>Exporta listas limpias de enlaces desde HTML guardados de canales de YouTube mediante una Agent Skill reutilizable.</strong></p>

  <p>
    <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-est%C3%A1ndar%20abierto-ff3355?style=flat-square"></a>
    <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
    <img alt="Sin red" src="https://img.shields.io/badge/red-ninguna-238636?style=flat-square">
    <a href="LICENSE"><img alt="Licencia MIT" src="https://img.shields.io/badge/licencia-MIT-f0f6fc?style=flat-square"></a>
  </p>

  <p><a href="README.md">English documentation</a></p>
</div>

## ¿Qué es?

YouTube Channel Link Exporter es una Agent Skill portable que recibe uno o varios archivos HTML guardados desde la pestaña **Videos** de un canal de YouTube y genera archivos `.txt` UTF-8 con un enlace canónico por renglón.

La IA interpreta los parámetros que indique el usuario. Un script determinista de Python realiza la extracción, deduplicación, validación del periodo y escritura de archivos sin gastar contexto del modelo en analizar manualmente HTML repetitivo.

Exporta **únicamente enlaces**. No descarga los archivos de video.

## Características

- Uno o varios HTML de canales por ejecución.
- Detección automática del nombre del canal.
- URLs canónicas `watch?v=` y opción para conservar URLs nativas de Shorts.
- Eliminación de duplicados sin alterar el orden guardado de la página.
- Filtrado temporal aproximado, por ejemplo `90d`, `6mo` o `4y`.
- Validación de que el HTML cargado alcance el periodo solicitado.
- Fechas relativas en español e inglés.
- Destinos predeterminados seguros en Windows, macOS y Linux.
- Ejecución local, sin dependencias externas ni solicitudes de red.

## Cómo guardar un HTML utilizable

YouTube carga dinámicamente las tarjetas del canal. Antes de guardar la página:

1. Abre la pestaña **Videos** del canal.
2. Selecciona el orden deseado.
3. Baja hasta que se hayan cargado todos los videos necesarios.
4. Espera a que termine la carga.
5. Guarda la página completa como HTML.

El archivo guardado contiene únicamente las tarjetas que ya estaban cargadas. La skill puede validar si cubren el periodo solicitado, pero no puede recuperar videos ausentes del HTML.

## Instalación

Clona o descarga este repositorio y coloca la carpeta completa dentro del directorio de skills compatible con tu agente. Conserva este nombre:

```text
youtube-channel-link-exporter
```

También puede usarse directamente con Python 3.10 o posterior:

```bash
python scripts/export_channel_links.py --help
```

## Ejemplos en lenguaje natural

```text
Extrae todos los enlaces cargados de este HTML de un canal.
```

```text
Usa estos tres HTML de canales de YouTube y guarda un TXT por canal en D:\Investigación\Fuentes.
```

```text
Exporta solo los videos de aproximadamente los últimos cuatro años, del más reciente al más antiguo. No aceptes un HTML parcial.
```

## Comportamiento predeterminado

| Entrada | Salida |
|---|---|
| Un HTML | `Escritorio/<Nombre del Canal>.txt` |
| Varios HTML | `Escritorio/YouTube Channel Link Exporter/<Nombre del Canal>.txt` |

Los archivos contienen solamente URLs, una por línea, sin títulos, numeración ni encabezados.

## Privacidad

- El HTML se procesa como datos inertes.
- No se ejecuta JavaScript embebido.
- No se realizan solicitudes de red.
- No se requieren credenciales, cookies ni sesiones del navegador.
- No se sobrescriben archivos existentes salvo que el usuario lo solicite.

## Desarrollo

```bash
python -m unittest discover -s tests -v
python scripts/check_repository.py
python scripts/package_skill.py
```

## Licencia

Se distribuye bajo la [licencia MIT](LICENSE).

## Aviso de marca

YouTube es una marca de Google LLC. Este proyecto es independiente, no está respaldado por Google y trabaja únicamente con archivos HTML guardados por el usuario.
