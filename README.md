# Proyecto MDV en Python

Este proyecto implementa una estructura `MDV` simple en Python:

- `Modelo`: define las entidades del dominio.
- `Datos`: guarda y recupera informacion.
- `Vista`: interactua con el usuario.

La aplicacion incluida permite registrar tareas desde consola y almacenarlas en un archivo JSON local.

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
- `view`: muestra menus y resultados por consola.

La documentacion detallada esta en la carpeta `docs/` y en los `README.md` internos de cada modulo.
