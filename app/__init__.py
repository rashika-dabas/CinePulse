from flask import Flask
from .routes import init_routes


def create_app():
    app = Flask(__name__, static_folder='static/build')

    # Import and initialize routes
    init_routes(app)

    return app
