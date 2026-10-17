from models import init_db as create_tables
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import Config

def init_db():
    # Crear tablas
    create_tables()
    
    # Insertar usuario admin si no existe
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        password_hashed = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@cryptobank.com', password_hashed, datetime.now().isoformat()))
        print("✅ Usuario admin creado")
    else:
        print("ℹ️ Usuario admin ya existe")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")

if __name__ == '__main__':
    init_db()
