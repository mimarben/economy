🟢 Fase 1 — Infraestructura LLM limpia

Objetivo: aprender LLM deployment.

Implementa:

Qwen vía llama.cpp

Endpoint /classify

Validación estricta JSON

Fallback a reglas

Batch classification

Aprendizaje:

Docker ML

Prompt engineering

Latencia

Gestión memoria

Diseño desacoplado

Esto ya es sólido.

🟡 Fase 2 — Dataset de correcciones (sin entrenar aún)

Cuando el usuario cambie algo:

Guarda en tabla nueva:

classification_feedback
---------------------------------
description
amount
predicted_type
predicted_category
corrected_type
corrected_category
timestamp


Todavía no entrenas nada.

Solo acumulas datos.

Aprendizaje:

Diseño de dataset real

Ingeniería de features

Preparación de datos

🔵 Fase 3 — Modelo pequeño entrenado por ti

Cuando tengas 1000+ ejemplos:

Entrenas:

fastText

scikit-learn (LogisticRegression)

o tiny transformer

Este modelo:

Es específico para tus datos

Mucho más rápido que LLM

Más preciso en tu caso concreto

Arquitectura híbrida profesional:

if modelo_personal_confianza > threshold:
    usar modelo_personal
else:
    usar LLM


Eso ya es arquitectura avanzada.

🎓 Qué aprendes realmente con ese enfoque

LLM deployment

Dataset design

Entrenamiento supervisado

Métricas (accuracy, precision, recall)

Gestión de versiones de modelo

Arquitectura híbrida ML

Eso es aprendizaje serio.
