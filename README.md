# Proyecto MDV en Python

Este proyecto implementa una estructura `MDV` simple en Python:

- `Modelo`: define las entidades del dominio.
- `Datos`: guarda y recupera informacion.
- `Vista`: interactua con el usuario.

La aplicacion incluida ofrece una interfaz visual de escritorio para registrar, completar, reabrir y eliminar tareas usando almacenamiento JSON local.
Tambien permite asignar prioridad, fecha de vencimiento, busqueda por texto y filtros de estado.
La vista incluye edicion de tareas, notas, ordenamiento, alertas visuales para vencimientos y selector de tema.

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

## Control de versiones

El historial funcional y la numeracion de versiones se documentan en `VERSIONES.md`.

## Seguridad

Para auditar vulnerabilidades conocidas en las dependencias declaradas:

```bash
python -m pip_audit -r requirements.txt
```

Actualmente el proyecto fue revisado con `pip-audit` sin hallazgos conocidos.

La documentacion detallada esta en la carpeta `docs/` y en los `README.md` internos de cada modulo.
