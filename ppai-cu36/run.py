import sys

from app import create_app

app = create_app()

if __name__ == "__main__":
    if "--seed" in sys.argv:
        from app.persistencia.seed import cargarDatos
        with app.app_context():
            cargarDatos()
        print("Datos de prueba cargados.")
    app.run(host="127.0.0.1", port=5000, debug=False)
