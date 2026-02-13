# Angular Material theme usage

This project uses a single class-based theme:

- `theme-economy`

## Active class
`src/index.html`:

```html
<body class="mat-typography theme-economy">
```

## What is customized (deep visual layer)
- Typography (Inter + Roboto)
- Button shape/weight/shadows (raised, outlined, unelevated, fab)
- Card radius/shadow/title hierarchy
- Table header style, hover and paginator border
- Form field outline/focus/shape tokens
- Chip and dialog rounded surfaces
- Sidebar and shell tokens

## Notes
- This keeps Angular Material components and behavior.
- No TypeScript business logic changes are required for these visual updates.
