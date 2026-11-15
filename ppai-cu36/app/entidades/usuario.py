from app.persistencia.db import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nombreUsuario = db.Column(db.String(50), unique=True, nullable=False)

    def getNombreUsuario(self) -> str:
        return self.nombreUsuario
