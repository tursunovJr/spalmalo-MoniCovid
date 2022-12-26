from flask import Flask, send_from_directory
import os
# from flask_swagger_ui import get_swaggerui_blueprint
from api import UserLogIn

SECRET_KEY = os.urandom(32)
CONFIG_NAME_MAPPER = {
    "testing": "config.TestingConfig",
    "production": "config.ProductionConfig",
}


def create_app(config_name=None):
    app = Flask(__name__)


    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    # SWAGGER_URL = '/swagger'
    # API_URL = '/static/swagger.json'
    # swaggerui_blueprint = get_swaggerui_blueprint(
    #     SWAGGER_URL,
    #     API_URL,
    #     config={
    #         'app_name':"MedLight API"
    #     }
    # )

    if config_name is None:
        config_name = "production"


    app.config.from_object(CONFIG_NAME_MAPPER[config_name])
    app.config['SECRET_KEY'] = SECRET_KEY

    # Register extensions
    from extensions import db, cors, ma, login_manager
    db.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'api.userlogin'

    # Register Blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    # app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    return app
