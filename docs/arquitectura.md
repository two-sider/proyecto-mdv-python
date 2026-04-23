# Arquitectura MDV

El proyecto usa una separacion sencilla en tres capas:

## Modelo

Contiene las entidades del dominio. En este caso, una tarea con:

- identificador
- titulo
- estado de completado
- prioridad
- fecha de vencimiento opcional
- notas opcionales

## Datos

Gestiona la lectura y escritura en `storage/tasks.json`, incluyendo el estado, prioridad, fecha y notas de cada tarea.

## Vista

Presenta una interfaz grafica de escritorio, recoge acciones del usuario y muestra resultados en tiempo real.
Tambien aplica filtros, ordenamiento y alertas visuales en la tabla de tareas.

## Observabilidad

La aplicacion registra eventos y errores en `logs/taskflow.log` para facilitar revision de fallos y seguimiento basico de uso.

## Beneficio

Esta division permite cambiar la persistencia o la interfaz sin romper la logica del dominio.
