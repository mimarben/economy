http://localhost:8000/docs
http://localhost:8000/redoc

# Documentation

[Pydantic and SqlAlchemi](https://medium.com/@melthaw/using-pydantic-for-data-validation-with-sqlalchemy-b15e4497cfb4)

for babel

```
pybabel extract -F babel.cfg -o messages.pot .

pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l es


pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l en
pybabel init -i messages.pot -d /home/miguel/src/economy/api/i18n -l es

# Compile to view the text modifications
pybabel compile -d /home/miguel/src/economy/api/i18n

```

for alembic

 ```
 alembic init alembic
 alembic revision --autogenerate -m "Name nullable-false" 

 alembic upgrade head

 # Upgrade to the latest revision
alembic upgrade head

# Upgrade to a specific revision
alembic upgrade <revision_id>

# Check current revision
alembic current

# Downgrade to a specific revision
alembic downgrade <revision_id>

# Pydantic

https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic

uv venv /home/miguel/venvs/economy-env --python 3.13.7

source /home/miguel/venvs/economy-env/bin/activate

uv sync --active

python app.py tiene que tener la ruta de la base de datos en la variable de entrono.

No funciona bien el uv en nfs ni samba o no lo he conseguido arreglar



uv pip compile pyproject.toml --output-file requirements.txt  


Con Docker
docker build -t flask-dev .
docker run -p 5001:5001 --env-file .env flask-dev
