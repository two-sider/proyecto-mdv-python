# Arquitectura MDV

El proyecto usa una separacion sencilla en tres capas:

## Modelo

Contiene las entidades del dominio. En este caso, una tarea con:

- identificador
- titulo
- estado de completado

## Datos

Gestiona la lectura y escritura en `storage/tasks.json`.

## Vista

Presenta un menu de consola, recoge entradas del usuario y muestra resultados.

## Beneficio

Esta division permite cambiar la persistencia o la interfaz sin romper la logica del dominio.
