from app.persistencia.db import db


class Empleado(db.Model):
    __tablename__ = "empleado"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    apellido = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100))

    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"), nullable=False)
    comision_medica_id = db.Column(db.Integer, db.ForeignKey("comision_medica.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)

    rol = db.relationship("Rol", lazy="selectin")
    asignadoA = db.relationship("ComisionMedica", lazy="selectin")
    usuario = db.relationship("Usuario", lazy="selectin")

    def esTuUsuario(self, usuario) -> bool:
        return self.usuario is not None and self.usuario.id == usuario.id

    def getCM(self):
        return self.asignadoA

    def sosCMDestino(self, cm) -> bool:
        """True si el empleado pertenece a la CM destino recibida por parámetro."""
        return self.asignadoA.getCodigo() == cm.getCodigo()

    def sosGCM(self) -> bool:
        return self.rol.esGCM()

    def getEmail(self) -> str:
        return self.email

    def getNombreCompleto(self) -> str:
        return f"{self.nombre} {self.apellido}"
