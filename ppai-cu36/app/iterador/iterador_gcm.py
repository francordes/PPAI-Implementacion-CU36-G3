from app.iterador.iiterador import IIterador


class IteradorGCM(IIterador):
    """--- Patrón Iterator --- Iterador concreto (fabricación pura).

    Recorre la colección de empleados y devuelve el que pertenece a la CM destino
    del bolsín seleccionado y tiene rol de Gerente de Comisión Médica.
    filtros[0] = ComisionMedica destino del bolsín seleccionado.
    """

    def __init__(self, elementos: list, filtros: list):
        # new(elementos: Object[], filtros: Object[]): IteradorGCM
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
        empleado = self._elementos[self._posicionActual]
        cmDestino = self._filtros[0]
        # sosCMDestino() y sosGCM() (-> Rol.esGCM())
        return empleado.sosCMDestino(cmDestino) and empleado.sosGCM()
