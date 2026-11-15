import requests
from flask import current_app


class InterfazGPS:
    """Boundary con el actor GPS Tracker modelo XTR-4500L (API mock de la cátedra)."""

    ENDPOINT = "/api/xtr-4500l/getBolsinLocation"

    def solicitarDatosLocalizacion(self, datosBolsines: list) -> dict:
        """Solicita la ubicación de cada bolsín (*getBolsinLocation()).

        datosBolsines: lista de dicts {numeroBolsin, codigoCMOrigen}.
        Retorna {"localizados": [...], "sinUbicacion": [nros]}.
        """
        localizados = []
        sinUbicacion = []
        for dato in datosBolsines:
            ubicacion = self._getBolsinLocation(dato["numeroBolsin"], dato["codigoCMOrigen"])
            if ubicacion is None:
                sinUbicacion.append(dato["numeroBolsin"])  # A3
            else:
                localizados.append(ubicacion)
        return {"localizados": localizados, "sinUbicacion": sinUbicacion}

    def _getBolsinLocation(self, numeroBolsin: int, codigoCMOrigen: str):
        url = current_app.config["GPS_API_URL"] + self.ENDPOINT
        headers = {"X-API-Key": current_app.config["GPS_API_KEY_XTR"]}
        params = {"numeroBolsin": numeroBolsin, "codigoComisionMedicaOrigen": codigoCMOrigen}
        try:
            respuesta = requests.get(
                url, headers=headers, params=params, timeout=current_app.config["GPS_API_TIMEOUT"]
            )
        except requests.RequestException as error:
            current_app.logger.warning("GPS Tracker sin respuesta para bolsín %s: %s", numeroBolsin, error)
            return None

        if respuesta.status_code != 200:
            current_app.logger.warning(
                "GPS Tracker respondió %s para bolsín %s: %s",
                respuesta.status_code, numeroBolsin, respuesta.text,
            )
            return None

        # Formato XTR-4500L: {"items": [{numeroBolsin, latitud, longitud, fechaHoraUltimaActualizacion}]}
        items = respuesta.json().get("items", [])
        if len(items) == 0:
            return None
        item = items[0]
        return {
            "numeroBolsin": int(item["numeroBolsin"]),
            "latitud": float(item["latitud"]),
            "longitud": float(item["longitud"]),
            "fechaHoraUltimaActualizacion": str(item["fechaHoraUltimaActualizacion"]),
        }
