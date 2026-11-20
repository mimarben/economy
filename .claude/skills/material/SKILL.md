---
name: material
description: Rediseño visual integral del cliente (referencia Ng-Matero; Finlytics y Notus secundarias) con Angular 21 + Angular Material + Tailwind CSS 4, sin romper funcionalidad existente. Usar para cualquier tarea de UI, estilos o layout.
---

# Rediseño integral de interfaz – Angular 21 + Angular Material + Tailwind CSS 4

## 1. Objetivo del proyecto

Quiero modernizar visualmente mi aplicación Angular actual siguiendo como referencia principal el dashboard de **Ng-Matero**.

Repositorio:
https://github.com/ng-matero/ng-matero

Demo:
https://ng-matero.github.io/ng-matero/dashboard

Usa como guía su dashboard, toolbar, navegación lateral, tarjetas y paneles de gráficos. Conserva la captura de Finlytics como referencia visual secundaria; Notus puede servir sólo como inspiración complementaria cuando aporte algo compatible.

La paleta debe evitar que toda la aplicación dependa del verde: usa azul/índigo como acento principal y reserva colores secundarios (morado, teal y verde) para jerarquía visual y significado. El verde semántico debe seguir indicando éxito; las superficies generales permanecen claras y los gráficos en paneles blancos.

**No instales Ng-Matero como una aplicación independiente ni copies sus componentes funcionales. Adapta sólo patrones visuales al proyecto actual y conserva los comportamientos existentes.**

## 2. Arquitectura que debes conservar

Mi aplicación ya está desarrollada y tiene bastante funcionalidad.

Stack tecnológico:

- Angular 21.
- Angular Material.
- Tailwind CSS 4.3.5.
- TypeScript.
- Dependencias y configuración actuales del proyecto.

Estas tecnologías deben mantenerse.

### Regla fundamental

No quiero sustituir Angular Material.

Angular Material seguirá siendo la biblioteca funcional de componentes de la aplicación.

Tailwind CSS será responsable de la maquetación, distribución, espaciado, responsive y presentación visual.

Ng-Matero será la referencia visual principal; Finlytics y Notus quedan como referencias complementarias.

## 3. Análisis de la referencia Ng-Matero

Consulta el repositorio oficial de Ng-Matero:

https://github.com/ng-matero/ng-matero

Y como inspiración complementaria, Notus Angular:

https://github.com/creativetimofficial/notus-angular

Puedes clonarlo en una carpeta temporal fuera del proyecto o utilizar GitHub para estudiar sus archivos.

Analiza especialmente:

- Layout administrativo.
- Sidebar.
- Navbar.
- Dashboard.
- Cards.
- Componentes visuales.
- Tablas.
- Formularios.
- Gráficos.
- Dropdowns.
- Menús.
- Iconografía.
- Sistema de colores.
- Estilos globales.
- Responsive.

Identifica qué componentes y patrones visuales pueden aprovecharse directamente y cuáles necesitan adaptación.

### Compatibilidad tecnológica

Las versiones y APIs del repositorio de referencia pueden diferir de las del proyecto. Comprueba su implementación actual y adapta sólo patrones visuales a Angular 21, Angular Material y Tailwind CSS 4.3.5.

Por tanto, antes de reutilizar código:

1. Inspecciona sus dependencias reales.
2. Comprueba sus versiones de Angular.
3. Comprueba su versión de Tailwind.
4. Analiza sus componentes y dependencias JavaScript.
5. Identifica incompatibilidades con Angular 21.
6. Identifica incompatibilidades con Tailwind CSS 4.3.5.
7. Adapta el código a las APIs y convenciones actuales.

NO copies su configuración antigua.

NO copies su package.json.

NO reemplaces angular.json, tsconfig.json ni la configuración actual de Tailwind.

NO instales versiones antiguas de dependencias.

NO incorpores dependencias adicionales sin justificación y aprobación.

Utiliza el código original como referencia, no como una aplicación que deba integrarse íntegramente.

## 4. Diseño visual que quiero conseguir

El resultado debe seguir la jerarquía visual de Ng-Matero, con Finlytics y Notus como inspiración secundaria cuando sean compatibles.

### Sidebar

- Navegación lateral moderna.
- Fondo blanco o ligeramente cálido.
- Logotipo y nombre de aplicación.
- Iconos lineales.
- Secciones de navegación agrupadas.
- Elemento activo destacado con un fondo suave.
- Separadores discretos.
- Sidebar contraíble.
- Responsive con menú adaptado a móviles.

### Navbar / Toolbar

- Barra superior limpia.
- Título de la sección actual.
- Búsqueda, notificaciones y perfil si ya existen.
- Separación visual discreta respecto al contenido.

### Área principal

- Fondo gris muy claro.
- Superficies blancas.
- Tarjetas con bordes sutiles.
- Esquinas ligeramente redondeadas.
- Sombras suaves.
- Espaciado generoso.
- Tipografía moderna.
- Jerarquía visual clara.

### Dashboard

- Tarjetas de indicadores.
- Cifras destacadas.
- Indicadores positivos y negativos.
- Gráficos limpios.
- Distribución equilibrada.
- Información organizada por importancia.

### Tablas

Mantener Angular Material Table.

Mejorar su presentación:

- Cabeceras discretas.
- Filas con espaciado adecuado.
- Bordes suaves.
- Hover.
- Filtros bien integrados.
- Paginación.
- Acciones contextuales.
- Estados vacíos.
- Estados de carga.

### Formularios

Mantener Angular Material Forms.

Mejorar:

- Distribución.
- Agrupación de campos.
- Espaciado.
- Etiquetas.
- Ayudas visuales.
- Validaciones.
- Estados de error.
- Botones principales y secundarios.

## 5. Integración con Angular Material

Esta condición es obligatoria.

Conserva los componentes Material que ya utiliza mi aplicación.

Por ejemplo:

- MatButton.
- MatFormField.
- MatInput.
- MatSelect.
- MatTable.
- MatPaginator.
- MatSort.
- MatDialog.
- MatMenu.
- MatSidenav.
- MatIcon.
- MatDatepicker.
- MatCheckbox.
- MatRadioButton.

No sustituyas sus funcionalidades por componentes propios de una referencia visual.

Puedes adaptar el HTML y las clases de presentación de las referencias para construir contenedores visuales alrededor de las plantillas existentes.

Si una referencia proporciona un dropdown, menú o modal, reproduce su apariencia utilizando Angular Material cuando ya exista un componente equivalente.

Evita duplicar funcionalidades.

## 6. Sistema de diseño

Construye un sistema visual reutilizable y centralizado.

Define:

- Paleta de colores.
- Tipografía.
- Tamaños de texto.
- Espaciados.
- Bordes.
- Radios.
- Sombras.
- Fondos.
- Tarjetas.
- Navegación.
- Estados hover.
- Estados activos.
- Estados de error.
- Estados deshabilitados.

Utiliza Tailwind CSS 4.3.5 y CSS propio cuando sea necesario.

Evita estilos duplicados y soluciones específicas para cada pantalla.

Comprueba especialmente las interacciones entre Tailwind Preflight y Angular Material.

No utilices !important de forma indiscriminada.

## 7. Protección de la aplicación existente

NO modificar la lógica de negocio.

NO modificar servicios ni llamadas API.

NO modificar modelos TypeScript.

NO modificar interfaces de datos.

NO modificar autenticación ni autorización.

NO modificar guards.

NO modificar rutas salvo que sea estrictamente necesario para el layout y esté justificado.

NO eliminar funcionalidades.

NO cambiar contratos entre componentes.

NO reemplazar formularios reactivos ni sus validaciones.

NO alterar filtros, ordenaciones ni paginaciones.

Conserva todos los bindings, eventos y comportamientos Angular existentes.

La prioridad es mejorar la experiencia de usuario sin romper el trabajo ya realizado.

## 8. Layout administrativo

El header y el footer deben cubrir el 100% del área situada a la derecha del sidenav.

- El sidenav tiene su propia altura completa y fondo continuo.
- El header ocupa el ancho disponible y debe compartir altura visual con la cabecera del sidenav.
- El footer ocupa el mismo ancho disponible y debe alinearse con el borde inferior del sidenav.
- El contenido principal no debe limitarse artificialmente salvo que una pantalla concreta lo requiera.
- No añadir bordes verdes decorativos a las uniones entre sidenav, header y footer.
- Los toasts de autenticación no deben permanecer después de redirigir al usuario.

## 9. Metodología de implementación

Quiero que trabajes por fases, pero no te limites a presentar un informe: una vez aprobado el análisis, debes realizar la implementación completa y comprobarla.

### Fase 1 – Auditoría

Inspecciona mi proyecto actual.

Analiza:

- Estructura de carpetas.
- Componentes.
- Layout.
- Rutas.
- Estilos globales.
- Configuración de Tailwind.
- Configuración de Angular Material.
- Componentes compartidos.
- Temas.
- Dependencias.

Analiza el dashboard y el código público de Ng-Matero como referencia visual.

### Fase 2 – Plan de integración

Presenta:

1. Qué patrones visuales de Ng-Matero adaptarás.
2. Qué elementos adaptarás.
3. Qué componentes Material conservarás.
4. Qué archivos actuales necesitarán modificaciones.

### Fase 3 – Implementación

Una vez aprobado el plan, realiza la implementación completa y compruébala. Trabaja en este orden:

1. Sistema de diseño (tokens de color, tipografía, espaciados, bordes, radios, sombras).
2. Layout general.
3. Sidebar.
4. Toolbar.
5. Área de contenido.
6. Tarjetas.
7. Tablas.
8. Formularios.
9. Diálogos y menús.
10. Responsive.

Conserva los componentes, selectores, bindings y eventos existentes. Si modificas una plantilla HTML, conserva íntegramente su comportamiento Angular.

### Fase 4 – Validación

- Compila con `ng build`: sin errores TypeScript ni de estilos.
- Las rutas siguen funcionando.
- Los formularios mantienen sus validaciones.
- Las tablas conservan filtros y paginación.
- Comprueba el comportamiento responsive.
- No se ha eliminado ninguna funcionalidad.

Corrige las regresiones introducidas por los cambios visuales.

## 10. Criterio de calidad

El resultado debe parecer una aplicación SaaS profesional desarrollada recientemente, no una aplicación Angular Material con otros colores: limpia, elegante, minimalista, con jerarquía visual clara y consistencia entre todas las pantallas.

**Prioridad absoluta: mejorar la experiencia de usuario sin romper ni reescribir el trabajo ya existente.**
