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