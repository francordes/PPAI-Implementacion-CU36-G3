from abc import ABC, abstractmethod


class IIterador(ABC):
    """--- Patrón Iterator --- Interfaz Iterador.

    El recorrido se implementa a mano con un índice (posicionActual).
    No se usan los iteradores del lenguaje (__iter__/__next__, generadores, for-in).
    """

    @abstractmethod
    def primero(self) -> None:
        """Posiciona el puntero en el primer elemento."""
        raise NotImplementedError

    @abstractmethod
    def siguiente(self) -> None:
        """Avanza el puntero a la siguiente posición."""
        raise NotImplementedError

    @abstractmethod
    def haFinalizado(self) -> bool:
        """True si no quedan elementos por recorrer."""
        raise NotImplementedError

    @abstractmethod
    def elementoActual(self) -> object:
        """Devuelve el elemento actual si cumple el filtro; si no, None."""
        raise NotImplementedError

    @abstractmethod
    def comprobarFiltro(self) -> bool:
        """Verifica si el elemento actual cumple los filtros del iterador."""
        raise NotImplementedError
