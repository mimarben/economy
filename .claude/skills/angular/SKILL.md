---
name: angular
description: Convenciones Angular 21 del proyecto Economy — signals en componentes nuevos, Angular Material + Tailwind CSS 4, ngx-translate, testing Jasmine. Usar para cualquier cambio en client/.
risk: safe
source: project
date_added: '2026-02-27'
---

# Angular 21 — convenciones del proyecto Economy

Guía a medida de este repositorio. NO es una guía genérica de Angular: refleja el stack real de `client/package.json` y las reglas de CLAUDE.md.

## Stack real

- Angular 21.2 + Angular CLI
- Angular Material 21 (+ material-moment-adapter) — única librería de componentes
- Tailwind CSS 4.3.5 (`@tailwindcss/postcss`) — layout, espaciado, responsive y presentación
- ngx-translate 17 — i18n `es`/`en` en `src/assets/i18n/`
- @ngxpert/hot-toast (toasts), chart.js + ng2-charts (gráficos), xlsx (import), lodash-es, date-fns
- zone.js — change detection clásica

**NO usar en este proyecto:** SSR/hydration, zoneless, NgModules nuevos, Bootstrap/PrimeNG/Nebular ni migrar componentes a otra librería de UI.

## Regla de oro (CLAUDE.md §9)

- Componentes NUEVOS → Signals: `signal`, `computed`, `input()`, `output()`, `inject()`.
- Componentes EXISTENTES → tocar lo mínimo necesario; NO migrarlos a signals por inercia.
- El código ya mezcla patrones: mantén coherencia con el componente en el que trabajas.

## Signals — patrones aprobados

```typescript
import { Component, signal, computed, input, output, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { AccountService } from '../../services/core/account.service';

@Component({ /* ... */ })
export class ExampleComponent {
  // HTTP: el servicio devuelve Observable → convertir a signal
  private accountService = inject(AccountService);
  accounts = toSignal(this.accountService.getAll(), { initialValue: [] });

  // Estado local
  selectedId = signal<number | null>(null);
  selected = computed(() => this.accounts().find(a => a.id === this.selectedId()));

  // Inputs / outputs
  accountId = input.required<number>();
  changed = output<number>();
}
```

### Signals vs RxJS — cuándo cada uno

| Caso                        | Usar                                       |
| --------------------------- | ------------------------------------------ |
| Estado local del componente | `signal` / `computed`                      |
| Valores derivados           | `computed()`                               |
| Peticiones HTTP             | Observable del servicio + `toSignal`       |
| Flujos complejos            | RxJS (`switchMap`, debounce...)            |
| Efectos secundarios         | `effect()` (con cuidado, evitar en cargas) |

## Control flow (plantillas nuevas)

Usar `@if` / `@for` / `@switch`:

```html
@if (accounts().length) {
  @for (a of accounts(); track a.id) {
    <tr>...</tr>
  } @empty {
    <tr><td>Sin datos</td></tr>
  }
} @else {
  <p>Cargando...</p>
}
```

- `track` es obligatorio en `@for` (usa el id de la entidad).
- Plantillas existentes usan `*ngIf="expr as alias"`; su equivalente moderno es `@if (expr; as alias)`.

## Componentes compartidos — reutilizar antes de crear

- `GenericTableComponent` (`shared/components/generic-table`) — tablas CRUD.
- `GenericFormComponent` (`shared/components/generic-form`) — formularios genéricos.
- Buscar en `shared/` antes de duplicar un patrón (regla CLAUDE.md §15).

## Tablas y formularios

- Tablas: MatTable + MatPaginator + MatSort (Angular Material).
- Formularios: Reactive Forms + MatFormField/MatInput/MatSelect/MatDatepicker/MatCheckbox.
- Diálogos: MatDialog. Toasts: `HotToastService`.

## i18n (ngx-translate)

- Toda cadena visible del usuario → clave en `src/assets/i18n/es.json` **y** `en.json` (mismo path en ambos).
- Uso: `{{ 'DASHBOARD.TITLE' | translate }}`.
- No hardcodear textos en plantillas ni en TS.

## Testing

- `ng test` (Karma/Jasmine). Componentes standalone: importar directo en TestBed.
- Inputs signal en tests: `fixture.componentRef.setInput('accountId', 5)`.

```typescript
await TestBed.configureTestingModule({ imports: [ExampleComponent] }).compileComponents();
const fixture = TestBed.createComponent(ExampleComponent);
fixture.componentRef.setInput('accountId', 5);
fixture.detectChanges();
```

## Reglas del proyecto que afectan al cliente

- No romper endpoints ni formatos de respuesta existentes (CLAUDE.md §10).
- No refactor global; extender lo existente (CLAUDE.md §0).
- Cambios visuales → seguir la skill `material` (rediseño activo Ng-Matero + Tailwind 4).
- Validar tras cambios: `npx tsc` y `ng build`.
