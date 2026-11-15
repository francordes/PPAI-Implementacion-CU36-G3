from abc import ABC, abstractmethod


class IAgregado(ABC):
    """--- Patrón Iterator --- Interfaz Agregado.

    Declara la operación para crear un iterador concreto sobre una colección.
    La implementación queda a cargo de los agregados concretos (GestorBolsines).
    """

    @abstractmethod
    def crearIterador(self, elementos: list):
        """Retorna un IIterador para recorrer 'elementos'."""
        raise NotImplementedError
