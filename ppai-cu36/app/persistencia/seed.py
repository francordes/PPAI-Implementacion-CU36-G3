"""Carga inicial de datos. Los bolsines 101-110 coinciden con los precargados en la API mock del GPS Tracker."""
from datetime import date, datetime, timedelta

from app.persistencia.db import db
from app.entidades import ComisionMedica, Estado, CambioEstado, Bolsin, Rol, Usuario, Empleado

COMISIONES = [
    ("CM-CBA-01", "CM Córdoba", "Av. Colón 1200, Córdoba"),
    ("CM-CBA-02", "CM Córdoba Norte", "Av. Monseñor Pablo Cabrera 3500, Córdoba"),
    ("CM-ROS-02", "CM Rosario", "Bv. Oroño 900, Rosario"),
    ("CM-MDZ-03", "CM Mendoza", "Av. San Martín 1500, Mendoza"),
    ("CM-BA-01", "CM Buenos Aires", "Av. de Mayo 700, CABA"),
    ("CM-TUC-01", "CM Tucumán", "Av. Sarmiento 400, San Miguel de Tucumán"),
    ("CM-SLA-01", "CM Salta", "Av. Belgrano 800, Salta"),
    ("CM-JUJ-01", "CM Jujuy", "Av. Senador Pérez 300, San Salvador de Jujuy"),
    ("CM-NQN-01", "CM Neuquén", "Av. Argentina 200, Neuquén"),
    ("CM-MDQ-01", "CM Mar del Plata", "Av. Luro 3000, Mar del Plata"),
    ("CM-LPL-01", "CM La Plata", "Calle 7 1000, La Plata"),
]

ESTADOS_BOLSIN = ["Creado", "Cerrado", "Enviado", "Recibido en CM destino", "De baja"]

ROLES = ["Encargado de Bolsines", "Gerente de Comisión Médica", "Encargado de Documentación"]

# (numeroBolsin, precinto, origen, destino, estadoActual)
BOLSINES = [
    (101, 5101, "CM-CBA-01", "CM-ROS-02", "Enviado"),
    (102, 5102, "CM-ROS-02", "CM-MDZ-03", "Enviado"),
    (103, 5103, "CM-MDZ-03", "CM-BA-01", "Enviado"),
    (104, 5104, "CM-BA-01", "CM-CBA-01", "Enviado"),
    (105, 5105, "CM-TUC-01", "CM-SLA-01", "Enviado"),
    (106, 5106, "CM-SLA-01", "CM-JUJ-01", "Enviado"),
    (107, 5107, "CM-NQN-01", "CM-MDQ-01", "Enviado"),
    (108, 5108, "CM-MDQ-01", "CM-BA-01", "Enviado"),
    (109, 5109, "CM-LPL-01", "CM-CBA-01", "Enviado"),
    (110, 5110, "CM-CBA-02", "CM-ROS-02", "Enviado"),
    # No existe en la API del GPS -> A3 (el GPS no pudo informar ubicación)
    (111, 5111, "CM-CBA-02", "CM-BA-01", "Enviado"),
    # De CM-CBA-01 pero NO enviados -> el iterador los descarta
    (112, 5112, "CM-CBA-01", "CM-MDZ-03", "Cerrado"),
    (113, 5113, "CM-CBA-01", "CM-ROS-02", "Recibido en CM destino"),
]

# Secuencia de estados por la que pasa un bolsín hasta su estado actual
SECUENCIA = ["Creado", "Cerrado", "Enviado", "Recibido en CM destino"]


def cargarDatos():
    db.drop_all()
    db.create_all()

    cms = {}
    for codigo, nombre, direccion in COMISIONES:
        sufijo = codigo.lower().replace("-", ".")
        cm = ComisionMedica(codigo=codigo, nombre=nombre, direccion=direccion,
                            email=f"{sufijo}@organismo.gob.ar", telefono="0800-000-0000")
        db.session.add(cm)
        cms[codigo] = cm

    estados = {}
    for nombre in ESTADOS_BOLSIN:
        estado = Estado(nombre=nombre, ambito=Estado.AMBITO_BOLSIN, descripcion=f"Bolsín {nombre.lower()}")
        db.session.add(estado)
        estados[nombre] = estado
    # Un estado "Enviado" de otro ámbito, para verificar que se filtra por ámbito
    db.session.add(Estado(nombre="Enviado", ambito="Remito", descripcion="Remito en bolsín enviado"))

    roles = {}
    for nombre in ROLES:
        rol = Rol(nombre=nombre, descripcion=nombre)
        db.session.add(rol)
        roles[nombre] = rol

    # Empleados: por cada CM un Encargado de Bolsines (con usuario) y un GCM (con usuario)
    empleadosEB = {}
    for codigo, nombre, _ in COMISIONES:
        ciudad = nombre.replace("CM ", "")
        sufijo = codigo.lower().replace("-", ".")

        usuarioEB = Usuario(nombreUsuario=f"eb.{sufijo}")
        eb = Empleado(nombre="Encargado", apellido=ciudad, email=f"eb.{sufijo}@organismo.gob.ar",
                      rol=roles["Encargado de Bolsines"], asignadoA=cms[codigo], usuario=usuarioEB)
        doc = Empleado(nombre="Documentación", apellido=ciudad, email=f"doc.{sufijo}@organismo.gob.ar",
                       rol=roles["Encargado de Documentación"], asignadoA=cms[codigo])
        usuarioGCM = Usuario(nombreUsuario=f"gcm.{sufijo}")
        gcm = Empleado(nombre="Gerente", apellido=ciudad, email=f"gcm.{sufijo}@organismo.gob.ar",
                       rol=roles["Gerente de Comisión Médica"], asignadoA=cms[codigo], usuario=usuarioGCM)
        db.session.add_all([usuarioEB, eb, doc, usuarioGCM, gcm])
        empleadosEB[codigo] = eb

    inicio = datetime(2026, 3, 5, 9, 0, 0)
    for numero, precinto, origen, destino, estadoActual in BOLSINES:
        bolsin = Bolsin(numeroBolsin=numero, numeroPrecinto=precinto, peso=850.0 + numero,
                        fecha=date(2026, 3, 5), origen=cms[origen], destino=cms[destino])
        db.session.add(bolsin)

        pasos = SECUENCIA[: SECUENCIA.index(estadoActual) + 1]
        momento = inicio + timedelta(minutes=numero)
        indice = 0
        while indice < len(pasos):
            fin = None if indice == len(pasos) - 1 else momento + timedelta(hours=6)
            responsable = empleadosEB[destino] if pasos[indice] == "Recibido en CM destino" else empleadosEB[origen]
            db.session.add(CambioEstado(bolsin_id=numero, fechaHoraInicio=momento, fechaHoraFin=fin,
                                        estado=estados[pasos[indice]], responsableCE=responsable))
            momento = momento + timedelta(hours=6)
            indice = indice + 1

    db.session.commit()
