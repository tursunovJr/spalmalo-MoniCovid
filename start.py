from app import create_app
from extensions import db
from os import getenv


app = create_app(getenv("FLASK_ENV", "production"))

with app.app_context():
    db.create_all()


app.run(host="0.0.0.0", port=8889)
