Proyecto presentado por Samuel Jiménez Robles para el bootcamp "Python Avanzado", de codigofacilito

Es un backend para un foro, que usa:
- Python 3.11.9 (muy probablemente es compatible con más versiones)
- FastAPI
- SQLModel

Y unas cuántas dependencias sólo para los tests:
- HTTPX (para poder usar el `fastapi.testclient.TestClient`)
- Pytest
- Faker

## Setup
Para poder ejecutar el proyecto, sigue los siguientes pasos
1. Crea un entorno virtual y actívalo. Yo uso venv para eso, y los comandos que pondré son para Linux
```bash
python -m venv .venv
```

2. Actívalo e instala las dependencias. `requirements-dev.txt` sólo es necesario si vas a ejecutar los tests
```bash
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

3. Ejecuta el archivo principal
```bash
python main.py
```

4. Visita http://localhost:3000/docs


Ahí mismo puedes ver los endpoints disponibles, el payload que pide cada uno, el método HTTP, los posibles errores, los esquemas...

### Variables de entorno
El proyecto no tiene ninguna variable de entorno obligatoria, pero tiene un sistema opcional muy chuli que las requiere

- SEND_REAL_EMAILS: Variable a la que le puedes poner cualquier valor, sólo se comprueba si existe
- GMAIL_ADDRESS: Dirección de correo gmail
- GMAIL_PASSWORD: No es la contraseña personal de la cuenta, sino una [contraseña de aplicación](https://support.google.com/accounts/answer/185833?hl=es)

Si quieres que el programa envíe enlaces de confirmación a la gente que se registra, tienes que asignar las 3 variables de arriba. Si no, el enlace sale en la consola. 
La idea es que uses lo segundo si sólo quieres ejecutar el proyecto en local para una prueba rápida

También hay un par más de configuración típicas, pero todas tienen valores por defecto:
- HOST
- PORT