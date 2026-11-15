from app.persistencia.db import db


class Rol(db.Model):
    __tablename__ = "rol"

    GERENTE_CM = "Gerente de Comisión Médica"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    descripcion = db.Column(db.String(150))

    def esGCM(self) -> bool:
        return self.nombre == Rol.GERENTE_CM
