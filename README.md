# TaskFlow MDV

Aplicacion de escritorio en Python para gestion de tareas, construida con arquitectura `MDV` (`Modelo`, `Datos`, `Vista`) y una interfaz visual hecha con `tkinter`.

## Caracteristicas

- creacion, edicion, completado, reapertura y eliminacion de tareas
- prioridad, fecha de vencimiento y notas por tarea
- filtros, busqueda y ordenamiento
- alertas visuales para tareas vencidas o proximas a vencer
- selector de tema con modos `clara`, `oscura` y `blue-coding`
- persistencia local en JSON
- logs en archivo
- ejecutable para Windows con `PyInstaller`

## Tecnologias

- Python 3.12
- tkinter
- pytest
- PyInstaller

## Arquitectura

El proyecto sigue una separacion `MDV`:

- `model`: entidades del dominio
- `data`: persistencia y configuracion
- `view`: interfaz grafica y flujo de interaccion

Estructura principal:

```text
proyecto-mdv-python/
|-- src/
|   |-- main.py
|   |-- model/
|   |-- data/
|   `-- view/
|-- docs/
|-- tests/
|-- storage/
|-- logs/
|-- VERSIONES.md
`-- requirements.txt
```

## Ejecucion

Desde la raiz del proyecto:

```bash
python -m src.main
```

## Ejecutable

Para generar el ejecutable de Windows:

```bash
python -m PyInstaller --name TaskFlowMDV --windowed --onefile src/main.py
```

El binario se genera en `dist/`.

## Configuracion

La aplicacion guarda datos locales en:

- `storage/tasks.json`: tareas
- `storage/settings.json`: preferencias visuales
- `logs/taskflow.log`: eventos y errores

## Versiones

El historial funcional y la numeracion de versiones se documentan en [VERSIONES.md](C:\Users\x13\proyecto-mdv-python\VERSIONES.md).

Version actual:

- `0.2.1`

## Seguridad

Para auditar vulnerabilidades conocidas en las dependencias declaradas:

```bash
python -m pip_audit -r requirements.txt
```

Estado actual:

- sin vulnerabilidades conocidas detectadas en la ultima revision con `pip-audit`

## Pruebas

Para ejecutar la suite:

```bash
python -m pytest -q
```

## Documentacion adicional

- `docs/`: arquitectura y flujo de la aplicacion
- `src/*/README.md`: descripcion breve por modulo

## Roadmap corto

- mejorar exportacion e importacion de tareas
- seguir refinando la experiencia visual
- ampliar configuraciones de usuario
