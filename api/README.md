http://localhost:8000/docs
http://localhost:8000/redoc

# Documentation

[Pydantic and SqlAlchemi](https://medium.com/@melthaw/using-pydantic-for-data-validation-with-sqlalchemy-b15e4497cfb4)

for babel



1️⃣ Extraer

```python
pybabel extract -F babel.cfg -o messages.pot .
```

✔ Se crea/actualiza:

/api/messages.pot

2️⃣ Actualizar idiomas

```python
pybabel update -i messages.pot -d i18n
```

✔ Actualiza:

/api/i18n/en/LC_MESSAGES/messages.po
/api/i18n/es/LC_MESSAGES/messages.po

Crea los mo
pybabel compile -d /home/miguel/src/economy/api/i18n


```python
pybabel compile -d /home/miguel/src/economy/api/i18n
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d i18n
```

## Solo la pimera vez.

```python
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l es
```

```python
pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l en
pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l es
```

# Compile to view the text modifications

```python
pybabel compile -d /home/miguel/src/economy/api/i18n
```




# ALEMBIC

```

for alembic cuando no hay base  de datos

```python
 alembic init alembic
 alembic revision --autogenerate -m "Name nullable-false"
 alembic upgrade head
```

 # Upgrade to the latest revision

```python
alembic upgrade head
```

# Upgrade to a specific revision
```python
alembic upgrade <revision_id>
```

# Check current revision

```python
alembic current
```

# Downgrade to a specific revision

```python
alembic downgrade <revision_id>
```

# Pydantic

https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic


# UV VENV

```python
uv venv /home/miguel/venvs/economy-env --python 3.13.7

source /home/miguel/venvs/economy-env/bin/activate

uv sync --active
```

python app.py tiene que tener la ruta de la base de datos en la variable de entrono.

No funciona bien el uv en nfs ni samba o no lo he conseguido arreglar


```python
uv pip compile pyproject.toml --output-file requirements.txt  
``

Con Docker

```python
docker build -t flask-dev .
docker run --rm -p 5001:5001 --env-file .env flask-dev
``

# Estructurra.

- Definir contratos formales

- Aplicar Interface Segregation Principle (ISP)

- Aplicar Dependency Inversion Principle (DIP)


# Router  →  Service  →  Repository  →  Database
