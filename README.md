# PPAI DSI 2026 – CU 36 Consultar seguimiento de bolsines (Patrón Iterator)

Guía rápida para levantar el proyecto el día de la defensa.

## Contenido del repositorio
```
PPAIEntrega/
├── dsi-api-bolsines-main/   ← API GPS Tracker de la cátedra (Java / Spring Boot)
└── ppai-cu36/               ← Nuestra aplicación (Python / Flask)
```

## Detalles de implementación
| Aspecto | Elección |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | Flask |
| Tecnología | Web |
| Base de datos | SQLite (`ppai-cu36/bolsines.db`) |
| Framework de persistencia | SQLAlchemy (Flask-SQLAlchemy) |
| GPS Tracker | API de la cátedra, modelo XTR-4500L |
| Mapa | Leaflet + OpenStreetMap |

---

## 0. Antes de ir a la facultad (en la PC donde se va a mostrar)
- [ ] **Python 3.11+** → https://www.python.org (tildar *"Add Python to PATH"*)
- [ ] **JDK 17** (no JRE) → https://adoptium.net/temurin/releases/?version=17
      → en el instalador activar **"Establecer la variable JAVA_HOME"**
- [ ] **Git** → https://git-scm.com
- [ ] Verificar en una terminal:
      ```
      python --version
      javac -version
      git --version
      ```
- [ ] Hacer una prueba completa (pasos 1 a 4) **con internet**: la primera vez se descargan dependencias.

## 1. Clonar el repositorio
⚠️ Usar una ruta **sin ñ, tildes ni espacios** (ej. `D:\ppai`).
```
cd D:\
git clone https://github.com/TU-USUARIO/TU-REPO.git ppai
cd ppai
```

## 2. Levantar la API del GPS (Terminal 1 — dejarla abierta)
En VS Code: **File → Open Folder → `ppai\dsi-api-bolsines-main`** → **Terminal → New Terminal**
```
.\mvnw.cmd spring-boot:run
```
✅ Lista cuando aparece: `Started GpsTrackerMockApplication`
✅ Comprobar en el navegador: http://localhost:8080/health → `{"status":"ok"}`

> Si dice `¿Desea terminar el trabajo por lotes (S/N)?` → responder **N**.
> No cerrar esta terminal ni apretar Ctrl+C.

## 3. Levantar la aplicación (Terminal 2)
En VS Code: **File → New Window → Open Folder → `ppai\ppai-cu36`** → **Terminal → New Terminal**

**Primera vez:**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py --seed
```
**Siguientes veces:**
```
venv\Scripts\activate
python run.py
```
✅ Lista cuando aparece: `Running on http://127.0.0.1:5000`

> `--seed` borra y vuelve a cargar los datos de prueba. Usarlo si algo quedó raro.

## 4. Abrir la aplicación
http://127.0.0.1:5000 → elegir usuario → **Ingresar** → **Consultar ubicación de bolsines**

---

## Guion para la defensa

### Flujos a mostrar
| Flujo | Usuario | Qué hacer | Qué se ve |
|---|---|---|---|
| **Descripto** | `eb.cm.cba.01` | Seleccionar bolsín 101 → **Sí, enviar correo** | Mensaje de éxito + `[CU31 simulado]` en la terminal |
| **A1** | `eb.cm.juj.01` | Consultar ubicación | "No se encontraron bolsines en estado Enviado" |
| **A2** | `eb.cm.cba.01` | Filtrar por precinto `9999` | "No se encontró bolsín con el número de precinto" |
| **A3 parcial** | `eb.cm.cba.02` | Consultar ubicación | Bolsín 110 en el mapa + aviso por el 111 |
| **A3 total** | cualquiera | Frenar la API (Ctrl+C en Terminal 1) y consultar | "El GPS Tracker no pudo informar la ubicación" |
| **A4** | cualquiera | Botón **Cancelar** | "Se canceló la consulta" |
| **A5** | `eb.cm.cba.01` | Seleccionar bolsín → **No enviar** | "No se envió el correo" |

> Para cambiar de usuario: **Salir** (arriba a la derecha).

### Dónde mostrar el Patrón Iterator
Buscar en VS Code (Ctrl+Shift+F): `Patrón Iterator`

| Archivo | Qué mostrar |
|---|---|
| `app/iterador/iagregado.py` | Interfaz `IAgregado` → `crearIterador()` |
| `app/iterador/iiterador.py` | Interfaz `IIterador` → `primero()`, `siguiente()`, `haFinalizado()`, `elementoActual()`, `comprobarFiltro()` |
| `app/iterador/iterador_bolsin_enviado.py` | Filtro: CM origen = CM del usuario **y** estado Enviado |
| `app/iterador/iterador_gcm.py` | Filtro: empleado de la CM destino **y** rol Gerente |
| `app/control/gestor_bolsines.py` | `selecOpcConsultarUbicacion()` (método de enganche), `crearIterador()`, `_buscarBolsinEnviadoDeCM()` y `_buscarGerenteDeCM()` con `while not iterador.haFinalizado()` |

Puntos clave para explicar:
- El recorrido es **propio** (índice `posicionActual`), no se usan iteradores del lenguaje.
- `GestorBolsines` **realiza** `IAgregado` y crea un iterador distinto según la colección.
- `elementoActual()` llama a `comprobarFiltro()`, que es **polimórfico** en cada iterador.

### Dónde mostrar la persistencia
- Entidades mapeadas con SQLAlchemy: `app/entidades/`
- Conexión: `app/persistencia/db.py` · Datos de prueba: `app/persistencia/seed.py`
- Ver la base en VS Code con la extensión **SQLite Viewer** → abrir `ppai-cu36/bolsines.db`

---

## Problemas frecuentes
| Error | Solución |
|---|---|
| `No compiler is provided ... JRE rather than a JDK` | Instalar el **JDK 17** (no JRE) y reiniciar VS Code |
| `javac` no se reconoce | Cerrar VS Code por completo y abrirlo de nuevo; si sigue, reiniciar la PC |
| `no se ha encontrado la clase principal GpsTrackerMockApplication` | Mover el proyecto a una ruta sin ñ ni espacios y correr `.\mvnw.cmd clean spring-boot:run` |
| `Port 8080 already in use` | Ya hay una API corriendo: cerrar la otra terminal |
| `la ejecución de scripts está deshabilitada` (al activar venv) | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y repetir |
| Todo da **A3** | La API no está levantada → revisar Terminal 1 y http://localhost:8080/health |
| El mapa se ve en blanco | Falta internet (Leaflet y OpenStreetMap se cargan desde la web) |
| La página se ve con el diseño viejo | Ctrl+F5 en el navegador |
| Aviso del Firewall de Windows para Java | Se puede cerrar: la app funciona igual en `localhost` |