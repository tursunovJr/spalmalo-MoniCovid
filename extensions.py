from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
cors = CORS(resource={r"/api/v1/*": {"origins": "*"}})
ma = Marshmallow()
login_manager = LoginManager()