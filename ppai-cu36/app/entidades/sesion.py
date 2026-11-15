from app.persistencia.db import db


class Sesion(db.Model):
    __tablename__ = "sesion"

    id = db.Column(db.Integer, primary_key=True)
    fechaHoraInicio = db.Column(db.DateTime, nullable=False)
    fechaHoraFin = db.Column(db.DateTime, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    usuario = db.relationship("Usuario", lazy="selectin")

    def getUsuario(self):
        return self.usuario
