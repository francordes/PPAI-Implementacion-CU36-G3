# PPAI DSI 2026 – CU 36 Consultar seguimiento de bolsines (Patrón Iterator)

## Detalles de implementación
| Aspecto | Elección |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | Flask 3 (plantillas Jinja2) |
| Tecnología | Web |
| Base de datos | SQLite (archivo `bolsines.db`) |
| Framework de persistencia | SQLAlchemy (Flask-SQLAlchemy) |
| GPS Tracker | API mock de la cátedra, modelo XTR-4500L (`getBolsinLocation`) |
| Mapa | Leaflet + OpenStreetMap, encapsulado en `InterfazGoogleMaps` |
| CU 31 Notificar ubicación | Simulado (se registra en consola/log) |

## Cómo ejecutar
1. **API del GPS Tracker** (Java 17), en otra terminal:
   ```bash
   git clone https://github.com/LiberaeMentis/dsi-api-bolsines
   cd dsi-api-bolsines
   ./mvnw spring-boot:run        # Windows: .\mvnw.cmd spring-boot:run
   ```
   Queda en `http://localhost:8080` (probar con `http://localhost:8080/health`).
2. **Aplicación**:
   ```bash
   python -m venv venv
   venv\Scripts\activate            # Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   python run.py --seed             # carga los datos de prueba y levanta la app
   ```
   Abrir `http://127.0.0.1:5000`. Las siguientes veces: `python run.py` (sin `--seed` conserva la BD).

Configuración opcional por variables de entorno: `GPS_API_URL`, `GPS_API_KEY_XTR`, `GPS_API_TIMEOUT`, `DATABASE_URL`.

## Usuarios para la demo
| Flujo | Usuario | Resultado esperado |
|---|---|---|
| Flujo descripto | `eb.cm.cba.01` | Mapa con el bolsín 101 → seleccionar → confirmar correo → notifica a `gcm.cm.ros.02` |
| A1 – sin bolsines enviados | `eb.cm.juj.01` | Mensaje A1 |
| A2 – precinto inexistente | `eb.cm.cba.01` | Filtrar por precinto `9999` |
| A3 – GPS no informa | `eb.cm.cba.01` (parcial: bolsín 111 no existe en la API) · o apagar la API (total) | Mensaje A3 |
| A4 – cancelar | cualquiera con bolsines | Botón **Cancelar** |
| A5 – no envía correo | `eb.cm.cba.01` | Seleccionar bolsín → **No enviar** |

Cada CM tiene un `eb.<cm>` (Encargado de Bolsines) y un `gcm.<cm>` (Gerente). En la BD, el usuario de CM-CBA-01 tiene además el bolsín 112 (Cerrado) y el 113 (Recibido), que el iterador descarta porque no están Enviados.

> Para tener más marcadores en el mapa se pueden agregar bolsines de `CM-CBA-01` en `InMemoryBolsinRepository.init()` de la API y en `app/persistencia/seed.py` con el mismo número.

## Estructura (consistente con el modelado)
```
app/
  boundary/    PantallaConsultarBolsines (rutas web), InterfazGPS, InterfazGoogleMaps
  control/     GestorBolsines, CU31NotificarUbicacionBolsin (simulado)
  iterador/    IAgregado, IIterador, IteradorBolsinEnviado, IteradorGCM
  entidades/   Bolsin, CambioEstado, Estado, ComisionMedica, Empleado, Rol, Usuario, Sesion
  persistencia/ db.py (SQLAlchemy), seed.py
```

## Patrón Iterator
- **Método de enganche**: `GestorBolsines.selecOpcConsultarUbicacion()`.
- `GestorBolsines` realiza `IAgregado` y en `crearIterador(elementos)` crea:
  - `IteradorBolsinEnviado` (filtro: CM del usuario) en `buscarBolsinEnviadoDeCM()`.
  - `IteradorGCM` (filtro: CM destino del bolsín seleccionado) en `buscarGerenteDeCM()`.
- Los iteradores recorren con un índice propio (`posicionActual`) y el gestor usa `while not iterador.haFinalizado()`; no se usan iteradores del lenguaje (`__iter__`, `__next__`, `yield`, `for ... in` sobre la colección).
- `elementoActual()` llama a `comprobarFiltro()`:
  - `IteradorBolsinEnviado`: `bolsin.esTuCMOrigen(cm)` y `bolsin.sosEnviado()` → `obtenerEstado()` → `*sosActual()` → `CambioEstado.sosEnviado()` → `Estado.sosEnviado()`.
  - `IteradorGCM`: `empleado.sosCMDestino(cm)` y `empleado.sosGCM()` → `Rol.esGCM()`.

## Decisiones respecto del modelado
- `ComisionMedica.codigo` es **String** (ej. `CM-CBA-01`) porque la API del GPS y el ERS lo exigen así; en la vista estática figura como `int`.
- La clase `CambioEstadoBolsin` del dominio se llama `CambioEstado`, igual que en la vista estática del rediseño.
- El CU 31 no es responsabilidad del CU 36: `llamarCU31()` solo simula la notificación.
