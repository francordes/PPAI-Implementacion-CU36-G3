from app.iterador.iiterador import IIterador


class IteradorBolsinEnviado(IIterador):
    """--- Patrón Iterator --- Iterador concreto (fabricación pura).

    Recorre la colección de bolsines y devuelve solo los que están en estado
    Enviado y cuya CM de origen es la CM del usuario logueado.
    filtros[0] = ComisionMedica del usuario logueado.
    """

    def __init__(self, elementos: list, filtros: list):
        # new(elementos: Object[], filtros: Object[]): IteradorBolsinEnviado
        self._elementos = elementos
        self._filtros = filtros
        self._posicionActual = 0

    def primero(self) -> None:
        self._posicionActual = 0

    def siguiente(self) -> None:
        self._posicionActual = self._posicionActual + 1

    def haFinalizado(self) -> bool:
        return self._posicionActual >= len(self._elementos)

    def elementoActual(self) -> object:
        if self.comprobarFiltro():
            return self._elementos[self._posicionActual]
        return None

    def comprobarFiltro(self) -> bool:
        bolsin = self._elementos[self._posicionActual]
        cmUsuario = self._filtros[0]
        # esTuCMOrigen() y sosEnviado() (-> obtenerEstado() -> *sosActual() -> sosEnviado())
        return bolsin.esTuCMOrigen(cmUsuario) and bolsin.sosEnviado()
