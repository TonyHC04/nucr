# NUCR · Economía interna escolar

> Proyecto escolar: una moneda digital interna para la universidad. Los alumnos ganan monedas por participación y calificaciones, y las canjean por cursos o trámites prioritarios.

![captura](docs/captura.png)

## Qué hace
- Registro e inicio de sesión de usuarios
- **Billetera** por usuario con saldo
- **Transferencias** entre usuarios e historial de transacciones
- **Precio de la moneda simulado** (fluctuación aleatoria) con gráfica histórica

## Cómo está hecho
| Capa | Tecnología |
|---|---|
| Backend | Python, Flask, Flask-Login |
| Base de datos | SQLite (capa de operaciones separada en `database/`) |
| Frontend | Plantillas Jinja2, CSS, JavaScript, gráficas |

## Correrlo localmente
```bash
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requeriments.txt
python database/init_db.py
python app.py                    # http://localhost:5000
```

## Autor
**Diego Antonio Hernández Chávez**, estudiante de Ciencia de Datos para Negocios (UNRC)
