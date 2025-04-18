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