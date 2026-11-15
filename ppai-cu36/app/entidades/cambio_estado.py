from app.persistencia.db import db


class CambioEstado(db.Model):
    """Cambio de estado de un Bolsín (CambioEstadoBolsin en el modelo de dominio)."""

    __tablename__ = "cambio_estado_bolsin"

    id = db.Column(db.Integer, primary_key=True)
    fechaHoraInicio = db.Column(db.DateTime, nullable=False)
    fechaHoraFin = db.Column(db.DateTime, nullable=True)

    bolsin_id = db.Column(db.Integer, db.ForeignKey("bolsin.numeroBolsin"), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey("estado.id"), nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey("empleado.id"), nullable=True)

    estado = db.relationship("Estado", lazy="selectin")
    responsableCE = db.relationship("Empleado", lazy="selectin")

    def sosActual(self) -> bool:
        # El cambio de estado actual es el que no tiene fecha/hora de fin
        return self.fechaHoraFin is None

    def sosEnviado(self) -> bool:
        # Delega en el Estado específico
        return self.estado.sosEnviado()

    def setFechaHoraFin(self, fechaHora) -> None:
        self.fechaHoraFin = fechaHora
