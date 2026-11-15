# Sistema Bolsines – CU 36 Consultar seguimiento de bolsines

PPAI 2026 · Diseño de Sistemas de Información · UTN FRC
| Curso | Grupo |
|---|---|
| 3K2 | G3 |

Implementación del **CU 36 Consultar seguimiento de bolsines** aplicando el **patrón Iterator**.
El Encargado de Bolsines ve en un mapa los bolsines enviados por su comisión médica que están en tránsito, selecciona uno y notifica su ubicación al Gerente de la comisión médica destino. La ubicación se obtiene de la API GPS Tracker provista por la cátedra.

## Tecnologías
| | |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | Flask |
| Tecnología | Web |
| Base de datos | SQLite |
| Persistencia | SQLAlchemy (ORM) |
| GPS Tracker | [API de la cátedra](https://github.com/LiberaeMentis/dsi-api-bolsines), modelo XTR-4500L |
| Mapa | Leaflet + OpenStreetMap |

## Patrón Iterator
El CU recorre dos colecciones con filtros distintos:
- los **bolsines**, para quedarse con los Enviados cuya CM origen es la del usuario;
- los **empleados**, para encontrar al Gerente de la CM destino.

El patrón saca ese recorrido y su filtrado del gestor y lo encapsula en iteradores con una interfaz común.

| Rol | Clase |
|---|---|
| Agregado (interfaz) | `IAgregado` |
| Iterador (interfaz) | `IIterador` |
| Agregado concreto | `GestorBolsines` (método de enganche: `selecOpcConsultarUbicacion()`) |
| Iteradores concretos | `IteradorBolsinEnviado`, `IteradorGCM` |

El recorrido está implementado a mano: un índice `posicionActual` y `while not iterador.haFinalizado()`, sin usar los iteradores del lenguaje. El código está en `ppai-cu36/app/iterador/` y en `ppai-cu36/app/control/gestor_bolsines.py`.

## Estructura
```
├── dsi-api-bolsines-main/      API GPS Tracker de la cátedra (Java 17)
└── ppai-cu36/                  Aplicación (Python)
    └── app/
        ├── boundary/           PantallaConsultarBolsines, InterfazGPS, InterfazGoogleMaps
        ├── control/            GestorBolsines
        ├── iterador/           IAgregado, IIterador, IteradorBolsinEnviado, IteradorGCM
        ├── entidades/          Bolsin, CambioEstado, Estado, ComisionMedica, Empleado, Rol, Usuario, Sesion
        └── persistencia/       Conexión ORM y datos de prueba
```

## Cómo ejecutarlo
**Requisitos:** Python 3.11+, JDK 17 y Git. Clonar el repositorio en una ruta sin ñ ni espacios.

**1. API GPS Tracker** (dejar la terminal abierta)
```bash
cd dsi-api-bolsines-main
.\mvnw.cmd spring-boot:run
```
Está lista cuando http://localhost:8080/health responde `{"status":"ok"}`.

**2. Aplicación** (en otra terminal)
```bash
cd ppai-cu36
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py --seed
```
Abrir http://127.0.0.1:5000. Las siguientes veces alcanza con `venv\Scripts\activate` y `python run.py`.

## Flujos implementados
| Flujo | Usuario | Cómo probarlo |
|---|---|---|
| Descripto | `eb.cm.cba.01` | Seleccionar el bolsín 101 → **Sí, enviar correo** |
| A1 – No hay bolsines enviados | `eb.cm.juj.01` | Consultar ubicación |
| A2 – Precinto no encontrado | `eb.cm.cba.01` | Filtrar por el precinto 9999 |
| A3 – El GPS no informa la ubicación | `eb.cm.cba.02` | El bolsín 111 no existe en la API (o detener la API) |
| A4 – El EB cancela | cualquiera | Botón **Cancelar** |
| A5 – No confirma el correo | `eb.cm.cba.01` | Seleccionar un bolsín → **No enviar** |

## Consideraciones
- `ComisionMedica.codigo` es **String** porque la API GPS lo exige en ese formato.
- El **CU 31 Notificar ubicación** está simulado: registra la notificación en la consola.
- El **inicio de sesión** es simulado: se elige el usuario.
- El mapa usa **Leaflet** y está encapsulado en `InterfazGoogleMaps`.
