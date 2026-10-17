# run_scripts.py

import sqlite3
import subprocess
import os
from datetime import datetime
from config import Config

# Lista de scripts a ejecutar (puedes modificar esta lista)
SCRIPTS = ['models.py']  # Cambia por los scripts reales que tienes

def crear_tabla_logs():
    """Crea la tabla donde se registran los logs de ejecución."""
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ejecuciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script TEXT,
                resultado TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def ejecutar_scripts():
    """Ejecuta los scripts definidos y guarda los resultados."""
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        for script in SCRIPTS:
            print(f"▶️ Ejecutando: {script}")
            if not os.path.exists(script):
                resultado = f"❌ ERROR: El archivo {script} no existe."
            else:
                try:
                    subprocess.run(['python', script], check=True)
                    resultado = "✅ ÉXITO"
                except subprocess.CalledProcessError as e:
                    resultado = f"❌ ERROR al ejecutar: {e}"
            cursor.execute('''
                INSERT INTO ejecuciones (script, resultado)
                VALUES (?, ?)
            ''', (script, resultado))
            print(f"   Resultado: {resultado}")
        conn.commit()

if __name__ == '__main__':
    crear_tabla_logs()
    ejecutar_scripts()
    print("\n🎉 Ejecución completada. Revisa la tabla 'ejecuciones' en la base de datos.")
