FROM python:3.13-slim


WORKDIR /app

# Copiar solo requirements.txt primero
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Usuario no privilegiado (uid/gid 1000 = usuario habitual del host,
# necesario porque docker-compose monta ./api en /app con permisos de escritura)
RUN groupadd -g 1000 app && useradd -u 1000 -g app -s /bin/bash app

# Copiar el resto del código
COPY --chown=app:app . .

USER app

# Exponer puerto
EXPOSE 5001

# FastAPI app (migrated from Flask; all routes are native now).
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]
