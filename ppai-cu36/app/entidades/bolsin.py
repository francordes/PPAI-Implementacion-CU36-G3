from app.persistencia.db import db


class Bolsin(db.Model):
    __tablename__ = "bolsin"

    numeroBolsin = db.Column(db.Integer, primary_key=True, autoincrement=False)
    peso = db.Column(db.Float)
    numeroPrecinto = db.Column(db.Integer)
    fecha = db.Column(db.Date)

    origen_id = db.Column(db.Integer, db.ForeignKey("comision_medica.id"), nullable=False)
    destino_id = db.Column(db.Integer, db.ForeignKey("comision_medica.id"), nullable=False)

    origen = db.relationship("ComisionMedica", foreign_keys=[origen_id], lazy="selectin")
    destino = db.relationship("ComisionMedica", foreign_keys=[destino_id], lazy="selectin")
    cambioEstado = db.relationship(
        "CambioEstado", lazy="selectin", order_by="CambioEstado.fechaHoraInicio"
    )

    # ---------- Métodos usados por el CU 36 ----------

    def esTuCMOrigen(self, cm) -> bool:
        """True si la CM de origen del bolsín es la CM recibida por parámetro."""
        return self.getCodigoCMOrigen() == cm.getCodigo()

    def _obtenerEstado(self):
        """Recorre sus cambios de estado (*sosActual) y devuelve el cambio de estado actual."""
        for cambio in self.cambioEstado:
            if cambio.sosActual():
                return cambio
        return None

    def sosEnviado(self) -> bool:
        actual = self._obtenerEstado()
        return actual is not None and actual.sosEnviado()

    def getNumeroBolsin(self) -> int:
        return self.numeroBolsin

    def getNroPrecinto(self) -> int:
        return self.numeroPrecinto

    def getCodigoCMOrigen(self) -> str:
        return self.origen.getCodigo()

    def obtenerCMDestino(self):
        return self.destino
