import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.persistencia.db import db
from app.entidades import Sesion, Usuario, Empleado
from app.control.gestor_bolsines import GestorBolsines

bp = Blueprint("pantalla", __name__)

# Una instancia de Pantalla (con su Gestor) por cada ejecución del CU, indexada por id de sesión web
_casosDeUsoActivos = {}


class PantallaConsultarBolsines:
    """«boundary» Pantalla del CU 36. Solo presentación: delega toda la lógica en el GestorBolsines."""

    def __init__(self, sesionActual):
        self.vista = {}
        self.gestor = GestorBolsines(self, sesionActual)

    # ---------- Acciones del actor (EB) ----------
    def selecOpcConsultarUbicacion(self) -> None:
        self.habilitarPantalla()
        self.gestor.selecOpcConsultarUbicacion()

    def tomarSeleccion(self, numeroBolsin: int) -> None:
        self.vista["mensajes"] = []
        self.gestor.tomarSeleccionBolsinMapa(numeroBolsin)

    def tomarConfirmacionEnvioCorreo(self, confirma: bool) -> None:
        self.gestor.tomarConfirmacionEnvioCorreo(confirma)

    def cancelar(self) -> None:
        self.gestor.cancelar()

    # ---------- Mensajes que recibe del gestor ----------
    def habilitarPantalla(self) -> None:
        self.vista = {
            "cmUsuario": None,
            "marcadores": [],
            "opciones": [],
            "mensajes": [],
            "confirmarCorreo": None,
            "exito": None,
        }

    def mostrarCMusuario(self, nombreCM: str) -> None:
        self.vista["cmUsuario"] = nombreCM

    def mostrarMapa(self, marcadores: list) -> None:
        self.vista["marcadores"] = marcadores

    def mostrarOpcionSeleccionarDesdeMapa(self) -> None:
        self.vista["opciones"].append("seleccionarDesdeMapa")

    def mostrarOpcionFiltrarPorNumero(self) -> None:
        self.vista["opciones"].append("filtrarPorNumero")

    def mostrarOpcionFiltrarPorCM(self) -> None:
        self.vista["opciones"].append("filtrarPorCM")

    def solicitarSeleccionOpcion(self) -> None:
        self.vista["solicitarSeleccion"] = True

    def solicitarEnvioCorreo(self, datosBolsin: dict) -> None:
        self.vista["confirmarCorreo"] = datosBolsin

    def mostrarMensajeDeExito(self, mensaje: str) -> None:
        self.vista["confirmarCorreo"] = None
        self.vista["exito"] = mensaje

    def mostrarMensajeAlternativo(self, codigo: str, mensaje: str) -> None:
        self.vista["mensajes"].append({"codigo": codigo, "texto": mensaje})
        if codigo in ("A4", "A5"):
            self.vista["confirmarCorreo"] = None

    # ---------- Filtros de presentación sobre el mapa ----------
    def filtrarMarcadores(self, precinto: str, cmDestino: str):
        marcadores = self.vista.get("marcadores", [])
        filtrados = []
        for marcador in marcadores:
            if precinto and str(marcador["numeroPrecinto"]) != precinto:
                continue
            if cmDestino and marcador["cmDestino"] != cmDestino:
                continue
            filtrados.append(marcador)
        mensajeFiltro = None
        if precinto and len(filtrados) == 0:
            # A2: No se encuentra bolsín con el número de precinto ingresado
            mensajeFiltro = {"codigo": "A2", "texto": f"No se encontró bolsín con el número de precinto {precinto}."}
        return filtrados, mensajeFiltro


# ======================================================================
# Rutas web
# ======================================================================
def _sesionActual():
    sesionId = session.get("sesion_id")
    if sesionId is None:
        return None
    return db.session.get(Sesion, sesionId)


def _pantallaActiva():
    return _casosDeUsoActivos.get(session.get("cu_id"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = db.session.get(Usuario, int(request.form["usuario_id"]))
        nuevaSesion = Sesion(fechaHoraInicio=datetime.now(), usuario=usuario)
        db.session.add(nuevaSesion)
        db.session.commit()
        session["sesion_id"] = nuevaSesion.id
        return redirect(url_for("pantalla.inicio"))
    empleados = Empleado.query.filter(Empleado.usuario_id.isnot(None)).order_by(Empleado.id).all()
    return render_template("login.html", empleados=empleados)


@bp.route("/logout")
def logout():
    sesionActual = _sesionActual()
    if sesionActual is not None:
        sesionActual.fechaHoraFin = datetime.now()
        db.session.commit()
    _casosDeUsoActivos.pop(session.get("cu_id"), None)
    session.clear()
    return redirect(url_for("pantalla.login"))


@bp.route("/")
def inicio():
    sesionActual = _sesionActual()
    if sesionActual is None:
        return redirect(url_for("pantalla.login"))
    return render_template("inicio.html", usuario=sesionActual.getUsuario().getNombreUsuario())


@bp.route("/consultar-ubicacion", methods=["POST"])
def selecOpcConsultarUbicacion():
    sesionActual = _sesionActual()
    if sesionActual is None:
        return redirect(url_for("pantalla.login"))
    _casosDeUsoActivos.pop(session.get("cu_id"), None)
    pantalla = PantallaConsultarBolsines(sesionActual)
    cuId = str(uuid.uuid4())
    _casosDeUsoActivos[cuId] = pantalla
    session["cu_id"] = cuId
    pantalla.selecOpcConsultarUbicacion()
    return redirect(url_for("pantalla.seguimiento"))


@bp.route("/seguimiento")
def seguimiento():
    pantalla = _pantallaActiva()
    if pantalla is None:
        return redirect(url_for("pantalla.inicio"))
    precinto = request.args.get("precinto", "").strip()
    cmDestino = request.args.get("cmDestino", "").strip()
    marcadores, mensajeFiltro = pantalla.filtrarMarcadores(precinto, cmDestino)
    cmsDestino = sorted({m["cmDestino"] for m in pantalla.vista.get("marcadores", [])})
    return render_template(
        "seguimiento.html",
        vista=pantalla.vista,
        marcadores=marcadores,
        mensajeFiltro=mensajeFiltro,
        precinto=precinto,
        cmDestino=cmDestino,
        cmsDestino=cmsDestino,
        finalizado=pantalla.gestor.finalizado,
    )


@bp.route("/seguimiento/seleccionar", methods=["POST"])
def tomarSeleccion():
    pantalla = _pantallaActiva()
    if pantalla is None or pantalla.gestor.finalizado:
        return redirect(url_for("pantalla.inicio"))
    pantalla.tomarSeleccion(int(request.form["numeroBolsin"]))
    return redirect(url_for("pantalla.seguimiento"))


@bp.route("/seguimiento/confirmar", methods=["POST"])
def tomarConfirmacionEnvioCorreo():
    pantalla = _pantallaActiva()
    if pantalla is None or pantalla.gestor.finalizado:
        return redirect(url_for("pantalla.inicio"))
    pantalla.tomarConfirmacionEnvioCorreo(request.form.get("confirma") == "si")
    return redirect(url_for("pantalla.seguimiento"))


@bp.route("/seguimiento/cancelar", methods=["POST"])
def cancelar():
    pantalla = _pantallaActiva()
    if pantalla is not None and not pantalla.gestor.finalizado:
        pantalla.cancelar()
    return redirect(url_for("pantalla.seguimiento"))
