class InterfazGoogleMaps:
    """Boundary con el actor Servidor de mapas.

    Prepara los marcadores que se dibujan en el mapa. La visualización se resuelve
    en el navegador con Leaflet + OpenStreetMap (no requiere API key); reemplazable
    por la librería de Google Maps sin modificar el gestor.
    """

    def mostrarEnMapa(self, bolsinesConLocalizacion: list) -> list:
        marcadores = []
        for bolsin in bolsinesConLocalizacion:
            marcadores.append({
                "numeroBolsin": bolsin["numeroBolsin"],
                "numeroPrecinto": bolsin["numeroPrecinto"],
                "cmDestino": bolsin["cmDestino"],
                "lat": bolsin["latitud"],
                "lng": bolsin["longitud"],
                "fechaHora": bolsin["fechaHoraUltimaActualizacion"],
            })
        return marcadores
