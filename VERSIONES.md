# Versiones

Este documento registra la evolucion funcional del proyecto.

## Esquema de versionado

Se usara el formato `MAJOR.MINOR.PATCH`.

- `MAJOR`: cambios grandes o incompatibles.
- `MINOR`: nuevas funciones sin romper compatibilidad.
- `PATCH`: correcciones, ajustes visuales o mejoras menores.

## Version actual

`0.1.0`

## Historial

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
