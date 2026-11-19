# Rediseño visual de la aplicación Angular – Referencia Finlytics

## Objetivo

Quiero realizar un rediseño visual completo de mi aplicación tomando como referencia la imagen adjunta (dashboard Finlytics).

**IMPORTANTE: quiero cambiar la apariencia y la experiencia de usuario, NO la arquitectura ni las tecnologías de mi aplicación.**

La aplicación ya está desarrollada y tiene bastante funcionalidad implementada. No quiero reconstruirla ni sustituir componentes que funcionan.

La imagen adjunta es la referencia estética que debes seguir.

## 1. Stack tecnológico actual

- Angular 21.
- Angular Material (utilizado directamente, sin otras bibliotecas de componentes).
- Tailwind CSS 4.3.5.
- TypeScript.
- Mantener todas las dependencias actuales.

No introducir Bootstrap, PrimeNG, Nebular, Materialize ni otras bibliotecas de componentes.

No sustituir Angular Material por otra solución.

## 2. Objetivo visual: reproducir el estilo de Finlytics

Analiza la imagen adjunta y utiliza su lenguaje visual como referencia.

Quiero conseguir una interfaz moderna, profesional y minimalista, similar a un dashboard SaaS financiero.

### Sidebar (menú lateral)

- Menú lateral vertical y persistente.
- Fondo blanco o ligeramente cálido.
- Logotipo y nombre de la aplicación en la parte superior.
- Navegación agrupada por secciones.
- Iconos lineales y minimalistas.
- Elemento activo claramente identificado mediante un fondo suave y un acento de color.
- Separación visual entre grupos de navegación.
- Posibilidad de contraer y expandir el menú.
- Diseño responsive: menú lateral adaptable en dispositivos pequeños.

### Toolbar superior

- Barra superior limpia y discreta.
- Título de la página actual.
- Espacio para búsqueda, notificaciones y perfil de usuario si existen actualmente.
- Separación sutil respecto al contenido.

### Área de contenido

- Fondo general gris muy claro.
- Tarjetas blancas.
- Bordes finos y discretos.
- Esquinas ligeramente redondeadas.
- Sombras muy suaves.
- Espaciado generoso y consistente.
- Buena jerarquía visual entre títulos, subtítulos y datos.

### Tarjetas e indicadores

- Métricas destacadas con números grandes.
- Etiquetas secundarias discretas.
- Indicadores de variación positivos y negativos.
- Iconografía sencilla.
- Evitar tarjetas excesivamente recargadas.

### Tablas

Mantener Angular Material Table, pero mejorar su presentación:

- Cabeceras limpias y discretas.
- Filas con altura y espaciado adecuados.
- Separadores sutiles.
- Estados hover.
- Estados vacíos bien diseñados.
- Filtros y paginación visualmente integrados.
- Acciones contextuales sin saturar la interfaz.

### Formularios

Mantener Angular Material Forms.

Mejorar:
- Distribución y alineación de campos.
- Espaciado entre controles.
- Agrupación lógica de campos.
- Etiquetas y ayudas visuales.
- Estados de validación.
- Botones principales y secundarios.

### Paleta de colores

Utilizar una paleta similar a la referencia:

- Fondo principal: gris muy claro.
- Superficies: blanco.
- Texto principal: gris muy oscuro.
- Texto secundario: gris medio.
- Color de acento: verde lima o verde suave.
- Estados positivos: verde.
- Estados negativos: rojo suave.
- Bordes: gris claro.

Evitar colores demasiado saturados y gradientes decorativos.

### Tipografía

Utilizar una tipografía moderna y legible.

Establecer una jerarquía consistente:
- Títulos de página.
- Títulos de sección.
- Subtítulos.
- Texto normal.
- Etiquetas y metadatos.

## 3. Reglas técnicas obligatorias

Esta parte es especialmente importante.

1. NO modificar la lógica de negocio.
2. NO modificar servicios ni acceso a APIs.
3. NO modificar modelos ni interfaces TypeScript.
4. NO modificar la estructura de datos.
5. NO modificar rutas ni guards.
6. NO modificar autenticación ni autorización.
7. NO eliminar funcionalidades existentes.
8. NO sustituir componentes Angular Material.
9. NO duplicar componentes existentes.
10. NO introducir dependencias nuevas sin una justificación técnica y mi aprobación.

Angular Material debe seguir siendo responsable de los componentes funcionales: botones, diálogos, tablas, formularios, selectores, menús, etc.

Tailwind CSS 4.3.5 debe utilizarse para layout, distribución, espaciado, responsive y presentación visual.

Puedes utilizar CSS/SCSS propio cuando sea necesario para personalizar Angular Material.

Evita utilizar `!important` indiscriminadamente.

Revisa especialmente la compatibilidad de Tailwind CSS 4 con los estilos de Angular Material y sus estilos de encapsulación.

## 4. Forma de trabajar

No realices una transformación masiva sin analizar primero el proyecto.

### Fase 1. Auditoría

Inspecciona:

- Estructura de carpetas.
- Configuración de Angular.
- Configuración de Tailwind CSS 4.3.5.
- Configuración de Angular Material.
- Estilos globales.
- Componentes compartidos.
- Layout actual.
- Sidebar y navegación.
- Toolbar.
- Componentes visuales reutilizables.
- Sistema actual de temas y colores.

Identifica qué estilos están duplicados, qué componentes tienen estilos propios y dónde conviene centralizar el diseño.

### Fase 2. Propuesta

Antes de modificar código, presenta:

1. Diagnóstico del diseño actual.
2. Archivos que necesitas modificar.
3. Componentes que necesitan cambios visuales.
4. Propuesta de estructura visual.
5. Estrategia para integrar Tailwind y Angular Material sin conflictos.
6. Riesgos de regresión funcional.

No cambies la arquitectura.

### Fase 3. Sistema de diseño

Establece una base visual reutilizable:

- Variables de color.
- Tipografía.
- Espaciados.
- Bordes.
- Radios.
- Sombras.
- Estilos de tarjetas.
- Estilos de navegación.
- Estados interactivos.

Centraliza los estilos comunes siempre que tenga sentido.

Evita soluciones específicas y duplicadas para cada pantalla.

### Fase 4. Implementación

Realiza el rediseño progresivamente.

Prioridad:

1. Layout general.
2. Sidebar.
3. Toolbar.
4. Área de contenido.
5. Tarjetas.
6. Tablas.
7. Formularios.
8. Diálogos y menús.
9. Responsive.

Conserva los componentes, selectores, bindings y eventos existentes.

Cuando sea necesario modificar una plantilla HTML, conserva íntegramente su comportamiento Angular.

### Fase 5. Validación

Al terminar:

- Ejecuta la compilación de Angular.
- Comprueba que no existen errores TypeScript.
- Comprueba que no hay errores de estilos.
- Comprueba que las rutas siguen funcionando.
- Comprueba que los formularios mantienen sus validaciones.
- Comprueba que las tablas conservan filtros y paginación.
- Comprueba el comportamiento responsive.
- Comprueba que no se han eliminado funcionalidades.

Soluciona los problemas introducidos por los cambios visuales.

## 5. Criterio de calidad

El resultado debe parecer una aplicación SaaS profesional desarrollada recientemente, no una aplicación Angular Material con unos colores diferentes.

Quiero conseguir la estética de Finlytics:

- Limpia.
- Elegante.
- Minimalista.
- Moderna.
- Buena jerarquía visual.
- Navegación intuitiva.
- Consistencia entre todas las pantallas.

La referencia es el diseño completo de la imagen adjunta, no solamente sus colores.

**Prioridad absoluta: mejorar la experiencia de usuario sin romper ni reescribir el trabajo que ya existe.**

## 6. Instrucción final

Empieza únicamente con la Fase 1 (auditoría) y la Fase 2 (propuesta).

No modifiques archivos hasta presentar el diagnóstico y la propuesta de implementación.

Después podremos ejecutar el rediseño por fases.
