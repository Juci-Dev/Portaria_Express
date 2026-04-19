from flask import Flask
from .morador_routes import morador_bp

def register_blueprints(app: Flask):
    app.register_blueprint(morador_bp, url_prefix='/morador')