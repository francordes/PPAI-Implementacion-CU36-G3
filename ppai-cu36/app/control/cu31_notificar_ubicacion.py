import logging

logger = logging.getLogger("CU31")


class CU31NotificarUbicacionBolsin:
    """Simulación del CU 31 Notificar ubicación de bolsín («include» desde el CU 36).

    No es responsabilidad del CU 36: solo se simula la notificación registrándola en el log.
    """

    def ejecutar(self, emailGCM: str, numeroBolsin: int, fechaHora: str, latitud: float, longitud: float) -> bool:
        logger.info(
            "[CU31 simulado] Notificación a %s -> Bolsín %s | Última actualización: %s | Coordenadas: (%s, %s)",
            emailGCM, numeroBolsin, fechaHora, latitud, longitud,
        )
        print(
            f"[CU31 simulado] Correo a {emailGCM}: bolsín {numeroBolsin}, "
            f"última actualización {fechaHora}, coordenadas ({latitud}, {longitud})"
        )
        return True
