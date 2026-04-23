# Modulo `data`

Esta capa se encarga de persistir y recuperar informacion.

## Archivo principal

- `task_repository.py`: administra el archivo `storage/tasks.json`.

## Responsabilidad

La capa de datos traduce entre objetos `Task` y JSON para que la vista no tenga que conocer detalles del almacenamiento.
