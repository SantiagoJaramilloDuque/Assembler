# Índice de Documentación

Este directorio contiene toda la documentación del ensamblador RISC-V. Aquí encontrarás desde guías básicas hasta referencias técnicas detalladas.

## Documentos Disponibles

### [README.md](../README.md) - Documentación Principal

- Descripción general del proyecto
- Instalación y configuración
- Uso básico del ensamblador
- Características principales
- Ejemplos rápidos

### [architecture.md](architecture.md) - Arquitectura del Sistema

- Diseño modular del proyecto
- Responsabilidades de cada módulo
- Flujo de datos y interacciones
- Patrones de diseño utilizados
- Guía para extensibilidad

### [isa-reference.md](isa-reference.md) - Referencia de Instrucciones

- Todas las instrucciones RV32I soportadas
- Pseudo-instrucciones implementadas
- Formatos de codificación
- Rangos válidos y restricciones
- Registros y convenios ABI

### [api-reference.md](api-reference.md) - Referencia de API

- Documentación completa de clases
- Métodos públicos y privados
- Parámetros y valores de retorno
- Ejemplos de uso programático
- Integración con Python

### [examples.md](examples.md) - Ejemplos Prácticos

- Programas de ejemplo paso a paso
- Casos de uso comunes
- Algoritmos implementados en RISC-V
- Manejo de errores
- Scripts de integración

### [testing.md](testing.md) - Guía de Testing

- Cómo ejecutar tests
- Escribir nuevos tests
- Mejores prácticas de testing
- Cobertura de código
- Integración continua

## Cómo Usar Esta Documentación

### Para Usuarios Nuevos

1. **Comienza con** [README.md](../README.md) para una visión general
2. **Sigue con** [examples.md](examples.md) para ver el ensamblador en acción
3. **Consulta** [isa-reference.md](isa-reference.md) para detalles de instrucciones

### Para Desarrolladores

1. **Lee** [architecture.md](architecture.md) para entender la estructura
2. **Consulta** [api-reference.md](api-reference.md) para integración
3. **Revisa** [testing.md](testing.md) antes de contribuir

### Para Referencia Rápida

- **Instrucciones disponibles**: [isa-reference.md](isa-reference.md)
- **API de clases**: [api-reference.md](api-reference.md)
- **Ejemplos de código**: [examples.md](examples.md)

## Convenciones de Documentación

### Formato

- Todos los documentos están en **Markdown**
- Uso de emojis para facilitar navegación
- Tablas para información estructurada
- Bloques de código con sintaxis destacada

### Estructura

- **Tabla de contenidos** al inicio
- **Secciones numeradas** con emojis
- **Ejemplos prácticos** en cada sección
- **Enlaces cruzados** entre documentos

### Código

- Ejemplos completos y ejecutables
- Comentarios explicativos
- Salidas esperadas mostradas
- Casos de error documentados

## Contribuir a la Documentación

### Reportar Problemas

Si encuentras errores o información desactualizada:

1. Abre un [issue](https://github.com/SantiagoJaramilloDuque/Assembler/issues)
2. Etiqueta como `documentation`
3. Describe el problema específico

### Mejorar la Documentación

Para contribuir mejoras:

1. Fork el repositorio
2. Edita los archivos Markdown correspondientes
3. Mantén el formato y estilo existente
4. Crea un Pull Request

### Agregar Nuevos Ejemplos

Los ejemplos son especialmente valiosos:

- Casos de uso reales
- Algoritmos interesantes
- Patrones de programación RISC-V
- Soluciones a problemas comunes

## Búsqueda Rápida

### Por Tema

| Necesitas                | Ver                                                           |
| ------------------------ | ------------------------------------------------------------- |
| Instalar el ensamblador  | [README.md](../README.md#instalación)                         |
| Lista de instrucciones   | [isa-reference.md](isa-reference.md#instrucciones-base-rv32i) |
| Pseudo-instrucciones     | [isa-reference.md](isa-reference.md#pseudo-instrucciones)     |
| Escribir un programa     | [examples.md](examples.md#ejemplo-básico)                     |
| Usar la API en Python    | [api-reference.md](api-reference.md#clase-ensamblador)        |
| Ejecutar tests           | [testing.md](testing.md#ejecutar-tests)                       |
| Entender la arquitectura | [architecture.md](architecture.md#visión-general)             |
| Manejar errores          | [examples.md](examples.md#detección-de-errores)               |

### Por Tipo de Usuario

| Eres                                        | Comienza aquí                                                               |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| **Estudiante** aprendiendo RISC-V           | [README.md](../README.md) → [examples.md](examples.md)                      |
| **Profesor** enseñando arquitectura         | [isa-reference.md](isa-reference.md) → [examples.md](examples.md)           |
| **Desarrollador** integrando el ensamblador | [api-reference.md](api-reference.md) → [architecture.md](architecture.md)   |
| **Contribuidor** al proyecto                | [architecture.md](architecture.md) → [testing.md](testing.md)               |
| **Usuario avanzado**                        | [isa-reference.md](isa-reference.md) → [api-reference.md](api-reference.md) |

## Estado de la Documentación

### Completitud

| Documento        | Estado   | Última actualización |
| ---------------- | -------- | -------------------- |
| README.md        | Completo | 2025-09-19           |
| architecture.md  | Completo | 2025-09-19           |
| isa-reference.md | Completo | 2025-09-19           |
| api-reference.md | Completo | 2025-09-19           |
| examples.md      | Completo | 2025-09-19           |
| testing.md       | Completo | 2025-09-19           |

### Cobertura

- **Instalación y configuración**
- **Uso básico y avanzado**
- **Referencia completa de API**
- **Ejemplos prácticos**
- **Guías de desarrollo**
- **Testing y calidad**

## Próximos Pasos

La documentación está completa y cubre todos los aspectos esenciales del ensamblador RISC-V. Para mantenerse actualizada:

1. **Revisar** con cada nueva característica
2. **Actualizar** ejemplos según feedback
3. **Expandir** basado en preguntas frecuentes
4. **Mantener** sincronización con el código

---

**¿No encuentras lo que buscas?** [Abre un issue](https://github.com/SantiagoJaramilloDuque/Assembler/issues) para solicitar documentación adicional.
