from app.persistencia.db import db


class Estado(db.Model):
    __tablename__ = "estado"

    AMBITO_BOLSIN = "Bolsin"
    ENVIADO = "Enviado"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    ambito = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.String(150))

    def sosEnviado(self) -> bool:
        return self.esAmbitoBolsin() and self.nombre == Estado.ENVIADO

    def esAmbitoBolsin(self) -> bool:
        return self.ambito == Estado.AMBITO_BOLSIN

    def getNombre(self) -> str:
        return self.nombre
