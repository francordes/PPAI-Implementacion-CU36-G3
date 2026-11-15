import logging

from flask import Flask

from config import Config
from app.persistencia.db import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    logging.basicConfig(level=logging.INFO)

    db.init_app(app)

    from app import entidades  # noqa: F401  (registra los modelos en el ORM)
    from app.boundary.pantalla_consultar_bolsines import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    @app.cli.command("seed")
    def seed():
        """Borra y vuelve a cargar los datos de prueba."""
        from app.persistencia.seed import cargarDatos
        cargarDatos()
        print("Datos de prueba cargados.")

    return app
