from flask import Flask
from .main import authenticate, bootstrap
import connexion


def create_app() -> connexion.FlaskApp:
    bootstrap()

    from .main.views.hotel import hotel_bp

    # app = Flask(__name__)
    # Create the application instance
    app = connexion.FlaskApp("__name__", specification_dir='./', options={"swagger_ui": True})
    # read the swagger to configure the endpoints
    app.add_api('swagger.yml')

    return app
