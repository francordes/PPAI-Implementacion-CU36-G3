from app.entidades import Bolsin, Empleado
from app.iterador import IAgregado, IteradorBolsinEnviado, IteradorGCM
from app.boundary.interfaz_gps import InterfazGPS
from app.boundary.interfaz_google_maps import InterfazGoogleMaps
from app.control.cu31_notificar_ubicacion import CU31NotificarUbicacionBolsin


class GestorBolsines(IAgregado):
    """«control» CU 36 Consultar seguimiento de bolsines.

    --- Patrón Iterator --- Agregado concreto: realiza la interfaz IAgregado.
    """

    def __init__(self, pantalla, sesionActual):
        self._pantalla = pantalla
        self._sesionActual = sesionActual
        self._interfazGPS = InterfazGPS()
        self._interfazGoogleMaps = InterfazGoogleMaps()

        # Atributos de la vista estática
        self.logueado = None                      # Empleado
        self.cmUsuario = None                     # ComisionMedica
        self.listaBolsines = []                   # Bolsin[]
        self.listaBolsinesEnviados = []           # Bolsin[]
        self.listaBolsinesConLocalizacion = []    # datos de localización por bolsín
        self.opcionSeleccionada = None            # str
        self.bolsinSeleccionado = None            # Bolsin
        self.cmDestino = None                     # ComisionMedica
        self.empleados = []                       # Empleado[]
        self.empleadoGCM = None                   # Empleado
        self.confirmacionEnvioCorreo = False      # bool
        self.emailGCM = None                      # str
        self.finalizado = False

    # ======================================================================
    # Método de enganche
    # ======================================================================
    def selecOpcConsultarUbicacion(self) -> None:
        self._obtenerUsuario()
        self._buscarCMusuario()
        self._buscarBolsinEnviadoDeCM()

        if len(self.listaBolsinesEnviados) == 0:
            # A1: No se encuentran bolsines en estado enviado
            self._pantalla.mostrarMensajeAlternativo(
                "A1", "No se encontraron bolsines en estado Enviado para su comisión médica."
            )
            self._finCU()
            return

        self._solicitarDatosLocalizacion()

        if len(self.listaBolsinesConLocalizacion) == 0:
            # A3: El GPS Tracker no pudo informar ubicación de ningún bolsín
            self._pantalla.mostrarMensajeAlternativo(
                "A3", "El GPS Tracker no pudo informar la ubicación de los bolsines."
            )
            self._finCU()
            return

        self._mapearBolsinesEnMapa()
        self._solicitarIngresoOpcion()

    # ======================================================================
    # Métodos conservados del análisis
    # ======================================================================
    def _obtenerUsuario(self) -> None:
        usuario = self._sesionActual.getUsuario()
        for empleado in Empleado.query.all():
            if empleado.esTuUsuario(usuario):  # *esTuUsuario()
                self.logueado = empleado
                return

    def _buscarCMusuario(self) -> None:
        self.cmUsuario = self.logueado.getCM()
        self._pantalla.mostrarCMusuario(self.cmUsuario.getNombre())

    # ======================================================================
    # --- Patrón Iterator --- recorrido de bolsines enviados
    # ======================================================================
    def _buscarBolsinEnviadoDeCM(self) -> None:
        self.listaBolsines = Bolsin.query.order_by(Bolsin.numeroBolsin).all()
        self.listaBolsinesEnviados = []
        self._datosBolsinesEnviados = []

        iterador = self.crearIterador(self.listaBolsines)
        iterador.primero()
        while not iterador.haFinalizado():
            bolsin = iterador.elementoActual()
            if bolsin is not None:
                self.listaBolsinesEnviados.append(bolsin)
                self._datosBolsinesEnviados.append({
                    "numeroBolsin": bolsin.getNumeroBolsin(),
                    "codigoCMOrigen": bolsin.getCodigoCMOrigen(),
                })
            iterador.siguiente()

    def crearIterador(self, elementos: list):
        """--- Patrón Iterator --- Método polimórfico de IAgregado.

        Crea el iterador concreto según la colección a recorrer:
        empleados -> IteradorGCM (filtro: CM destino del bolsín seleccionado)
        bolsines  -> IteradorBolsinEnviado (filtro: CM del usuario logueado)
        """
        if len(elementos) > 0 and isinstance(elementos[0], Empleado):
            return IteradorGCM(elementos, [self.cmDestino])
        return IteradorBolsinEnviado(elementos, [self.cmUsuario])

    # ======================================================================
    # Métodos conservados del análisis (solicitarDatosLocalizacion ... obtenerCMDestino)
    # ======================================================================
    def _solicitarDatosLocalizacion(self) -> None:
        respuesta = self._interfazGPS.solicitarDatosLocalizacion(self._datosBolsinesEnviados)
        self.listaBolsinesConLocalizacion = respuesta["localizados"]
        self._bolsinesSinUbicacion = respuesta["sinUbicacion"]

    def _mapearBolsinesEnMapa(self) -> None:
        datosMapa = []
        for localizacion in self.listaBolsinesConLocalizacion:
            bolsin = self._buscarBolsinEnviado(localizacion["numeroBolsin"])
            datosMapa.append({
                **localizacion,
                "numeroPrecinto": bolsin.getNroPrecinto(),
                "cmDestino": bolsin.obtenerCMDestino().getNombre(),
            })
        self._marcadores = self._interfazGoogleMaps.mostrarEnMapa(datosMapa)

    def _solicitarIngresoOpcion(self) -> None:
        self._pantalla.mostrarMapa(self._marcadores)
        if len(self._bolsinesSinUbicacion) > 0:
            # A3 parcial: se informa y se continúa con los bolsines localizados
            self._pantalla.mostrarMensajeAlternativo(
                "A3",
                "El GPS Tracker no pudo informar la ubicación de los bolsines: "
                + ", ".join(str(n) for n in self._bolsinesSinUbicacion),
            )
        self._pantalla.mostrarOpcionSeleccionarDesdeMapa()
        self._pantalla.mostrarOpcionFiltrarPorNumero()
        self._pantalla.mostrarOpcionFiltrarPorCM()
        self._pantalla.solicitarSeleccionOpcion()

    def tomarSeleccionBolsinMapa(self, numeroBolsin: int) -> None:
        self.opcionSeleccionada = "SeleccionarDesdeMapa"
        self.bolsinSeleccionado = self._buscarBolsinEnviado(numeroBolsin)
        if self.bolsinSeleccionado is None:
            return
        self._solicitarEnvioCorreoAGerente()

    def _solicitarEnvioCorreoAGerente(self) -> None:
        localizacion = self._buscarLocalizacion(self.bolsinSeleccionado.getNumeroBolsin())
        self._pantalla.solicitarEnvioCorreo({
            "numeroBolsin": self.bolsinSeleccionado.getNumeroBolsin(),
            "numeroPrecinto": self.bolsinSeleccionado.getNroPrecinto(),
            "cmDestino": self.bolsinSeleccionado.obtenerCMDestino().getNombre(),
            "fechaHora": localizacion["fechaHoraUltimaActualizacion"],
            "lat": localizacion["latitud"],
            "lng": localizacion["longitud"],
        })

    def tomarConfirmacionEnvioCorreo(self, confirma: bool) -> None:
        self.confirmacionEnvioCorreo = confirma
        if not confirma:
            # A5: El EB no selecciona la opción para enviar el correo
            self._pantalla.mostrarMensajeAlternativo(
                "A5", "No se envió el correo electrónico al Gerente de Comisión Médica."
            )
            self._finCU()
            return

        self._obtenerCMDestino()
        self._buscarGerenteDeCM()
        if self.empleadoGCM is None:
            self._pantalla.mostrarMensajeAlternativo(
                "Error", "No se encontró un Gerente de Comisión Médica para la CM destino."
            )
            self._finCU()
            return
        self._obtenerEmail()
        self._llamarCU31()

    def _obtenerCMDestino(self) -> None:
        self.cmDestino = self.bolsinSeleccionado.obtenerCMDestino()

    # ======================================================================
    # --- Patrón Iterator --- recorrido de empleados para encontrar al GCM
    # ======================================================================
    def _buscarGerenteDeCM(self) -> None:
        self.empleados = Empleado.query.order_by(Empleado.id).all()
        self.empleadoGCM = None

        iterador = self.crearIterador(self.empleados)
        iterador.primero()
        while not iterador.haFinalizado():
            empleado = iterador.elementoActual()
            if empleado is not None:
                self.empleadoGCM = empleado
            iterador.siguiente()

    def _obtenerEmail(self) -> None:
        self.emailGCM = self.empleadoGCM.getEmail()

    def _llamarCU31(self) -> None:
        localizacion = self._buscarLocalizacion(self.bolsinSeleccionado.getNumeroBolsin())
        exito = CU31NotificarUbicacionBolsin().ejecutar(
            self.emailGCM,
            self.bolsinSeleccionado.getNumeroBolsin(),
            localizacion["fechaHoraUltimaActualizacion"],
            localizacion["latitud"],
            localizacion["longitud"],
        )
        if exito:
            self._pantalla.mostrarMensajeDeExito(
                f"Se notificó la ubicación del bolsín {self.bolsinSeleccionado.getNumeroBolsin()} "
                f"al Gerente de Comisión Médica {self.empleadoGCM.getNombreCompleto()} ({self.emailGCM})."
            )
        self._finCU()

    def cancelar(self) -> None:
        # A4: El EB cancela la ejecución del caso de uso
        self._pantalla.mostrarMensajeAlternativo("A4", "Se canceló la consulta de seguimiento de bolsines.")
        self._finCU()

    def _finCU(self) -> None:
        self.finalizado = True

    # ======================================================================
    # Auxiliares
    # ======================================================================
    def _buscarBolsinEnviado(self, numeroBolsin: int):
        for bolsin in self.listaBolsinesEnviados:
            if bolsin.getNumeroBolsin() == numeroBolsin:
                return bolsin
        return None

    def _buscarLocalizacion(self, numeroBolsin: int):
        for localizacion in self.listaBolsinesConLocalizacion:
            if localizacion["numeroBolsin"] == numeroBolsin:
                return localizacion
        return None
