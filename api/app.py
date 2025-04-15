# app.py
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
from routers.users import router  # Import your routes

app = Flask(__name__)



# Register route blueprint
app.register_blueprint(router)

# Run app (optional if using a separate runner)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)