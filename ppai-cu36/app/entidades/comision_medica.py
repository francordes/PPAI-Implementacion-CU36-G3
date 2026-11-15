from app.persistencia.db import db


class ComisionMedica(db.Model):
    __tablename__ = "comision_medica"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    # El código se maneja como String porque la API del GPS Tracker lo exige en ese formato (ej. "CM-CBA-01")
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(150))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(30))

    def getCodigo(self) -> str:
        return self.codigo

    def getNombre(self) -> str:
        return self.nombre
