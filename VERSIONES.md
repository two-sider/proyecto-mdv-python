# Versiones

Este documento registra la evolucion funcional del proyecto.

## Esquema de versionado

Se usara el formato `MAJOR.MINOR.PATCH`.

- `MAJOR`: cambios grandes o incompatibles.
- `MINOR`: nuevas funciones sin romper compatibilidad.
- `PATCH`: correcciones, ajustes visuales o mejoras menores.

## Version actual

`0.2.1`

## Historial

### `0.2.1` - Temas configurables

Incluye:

- selector de tema con modos `clara`, `oscura` y `blue-coding`
- persistencia de configuracion visual en archivo
- aplicacion global del tema sobre la interfaz
- documentacion del flujo de auditoria de dependencias con `pip-audit`

### `0.2.0` - Gestion visual ampliada

Incluye:

- notas por tarea
- ordenamiento por fecha de creacion, prioridad, vencimiento, estado y titulo
- alertas visuales directamente en la tabla
- mejoras de usabilidad para planificacion diaria

### `0.1.0` - Primer MVP visual

Incluye:

- estructura MDV en Python
- aplicacion visual de escritorio con `tkinter`
- creacion, edicion, completado, reapertura y eliminacion de tareas
- prioridad, fecha de vencimiento, filtros y busqueda
- alertas de vencimiento
- logs en archivo
- ejecutable para Windows con `PyInstaller`

### Proxima regla de incremento

- si agregamos una funcion nueva importante: subir `MINOR`
- si corregimos errores o detalles de UI: subir `PATCH`
- si cambiamos la estructura de datos o rompemos compatibilidad: subir `MAJOR`
