# Flujo de la aplicacion

1. `src/main.py` crea la vista y el repositorio.
2. La vista solicita una accion al usuario desde la interfaz grafica.
3. La capa de datos guarda o recupera tareas con prioridad y fecha.
4. El modelo estandariza la estructura que circula entre capas.
5. La vista muestra el resultado final, los filtros activos y el detalle de la tarea seleccionada.

Este flujo mantiene responsabilidades separadas y hace mas simple extender el proyecto.
