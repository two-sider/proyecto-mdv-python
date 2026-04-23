# Modulo `view`

Esta capa interactua con el usuario.

## Archivo principal

- `task_manager_view.py`: crea una interfaz grafica con `tkinter` para gestionar tareas, editarlas, agregar notas, ordenar la tabla, cambiar de tema, ver alertas de vencimiento, aplicar filtros y desplazarse en pantallas pequenas.

## Responsabilidad

La vista no decide como se guardan los datos. Solo solicita acciones al repositorio y comunica el resultado mediante una ventana de escritorio.
