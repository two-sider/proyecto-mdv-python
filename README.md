# Proyecto MDV en Python

Este proyecto implementa una estructura `MDV` simple en Python:

- `Modelo`: define las entidades del dominio.
- `Datos`: guarda y recupera informacion.
- `Vista`: interactua con el usuario.

La aplicacion incluida ofrece una interfaz visual de escritorio para registrar, completar, reabrir y eliminar tareas usando almacenamiento JSON local.
Tambien permite asignar prioridad, fecha de vencimiento, busqueda por texto y filtros de estado.
La vista incluye edicion de tareas y alertas visuales para vencimientos.

## Estructura

```text
proyecto-mdv-python/
|-- src/
|   |-- main.py
|   |-- model/
|   |-- data/
|   `-- view/
|-- storage/
|-- docs/
|-- tests/
|-- .gitignore
`-- requirements.txt
```

## Ejecucion

```bash
python -m src.main
```

## Objetivo de cada capa

- `model`: representa la estructura de la informacion.
- `data`: se encarga de persistir las tareas.
- `view`: construye la interfaz grafica y refleja el estado actual de las tareas.

## Logs

Los eventos y errores de la aplicacion se escriben en `logs/taskflow.log`.

## Ejecutable

Para generar un ejecutable de Windows:

```bash
python -m PyInstaller --name TaskFlowMDV --windowed --onefile -m src.main
```

El binario quedara en `dist/`.

La documentacion detallada esta en la carpeta `docs/` y en los `README.md` internos de cada modulo.
