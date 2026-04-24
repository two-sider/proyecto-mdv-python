# Versiones

Este documento registra la evolucion funcional del proyecto.

## Esquema de versionado

Se usara el formato `MAJOR.MINOR.PATCH`.

- `MAJOR`: cambios grandes o incompatibles.
- `MINOR`: nuevas funciones sin romper compatibilidad.
- `PATCH`: correcciones, ajustes visuales o mejoras menores.

## Version actual

`0.6.0`

## Historial

### `0.6.0` - Comprobacion de actualizaciones

Incluye:

- verificacion de la ultima release disponible en GitHub al iniciar la app
- boton manual para buscar actualizaciones desde la interfaz
- acceso directo a la descarga de la ultima version publicada
- logica de comparacion de versiones sin dependencias externas

### `0.5.0` - Responsables y recarga externa

Incluye:

- campo `responsable` por tarea
- selector reutilizable con responsables ya usados previamente
- separacion visual entre `Filtro` y `Ordenar por`
- recarga manual y actualizacion automatica cuando cambia el archivo de tareas desde fuera de la app

### `0.4.0` - Sincronizacion con Google Drive

Incluye:

- seleccion de carpeta sincronizada de Google Drive desde la interfaz
- uso de `tasks.json` dentro de Google Drive como almacenamiento principal
- opcion para volver al almacenamiento local sin perder las tareas actuales
- persistencia de la carpeta de sincronizacion en configuracion local

### `0.3.1` - Ajustes de experiencia de uso

Incluye:

- boton para reiniciar filtros, orden y busqueda en un clic
- duplicado rapido de tareas desde el panel de acciones
- pruebas del repositorio para duplicacion de tareas

### `0.3.0` - Exportacion e importacion de tareas

Incluye:

- exportacion manual de tareas a archivo JSON desde la interfaz
- importacion de tareas desde respaldo JSON con opcion de reemplazar o fusionar
- normalizacion de identificadores al importar para evitar conflictos
- configuracion de `pytest` para ejecutar la suite en entornos con `Temp` restringido

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
