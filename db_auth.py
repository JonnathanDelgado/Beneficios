# logueos de sshtunnel a /dev/null
# Bug de Logeo se arregl desintalando la versión 4.0 de paramiko e instalando pip uninstall -y paramiko
# pip install "paramiko<3" sshtunnel mysql-connector-python   (Solución al Bug de error de logeo a pesar que esten bien las credenciales)
# timeouts recomendados por la guía
import MySQLdb
import sshtunnel
from typing import Tuple, Optional

# timeouts recomendados por la guía
sshtunnel.SSH_TIMEOUT = 10.0
sshtunnel.TUNNEL_TIMEOUT = 10.0

SSH_HOST = ('ssh.pythonanywhere.com', 22)
SSH_USER = 'GPON2'
SSH_PASS = 'z1x2c345'

REMOTE_DB_HOST = 'gpon2.mysql.pythonanywhere-services.com'
REMOTE_DB_PORT = 3306

DB_USER = 'GPON2'
DB_PASS = 'Mug1w@r@noluffy'
DB_NAME = 'GPON2$Usuarios'

def verify_login(usuario: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica credenciales contra la tabla `users` en MySQL usando SHA2-256.
    Retorna (ok, name): ok=True si coincide usuario+hash y name es el nombre del usuario.
    Si no coincide, retorna (False, None).
    """
    with sshtunnel.SSHTunnelForwarder(
        SSH_HOST,
        ssh_username=SSH_USER,
        ssh_password=SSH_PASS,
        remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
        allow_agent=False,
        host_pkey_directories=[],
    ) as tunnel:
        conn = MySQLdb.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=DB_USER,
            passwd=DB_PASS,
            db=DB_NAME,
            charset="utf8mb4",
        )
        try:
            cur = conn.cursor()
            # Seleccionamos el campo `name` si hay coincidencia
            cur.execute(
                "SELECT name FROM users WHERE usuario=%s AND password_hash = SHA2(%s, 256) LIMIT 1",
                (usuario, password)
            )
            row = cur.fetchone()
            cur.close()

            if row is not None:
                # row será una tupla, por ejemplo ('Juan Pérez',)
                return True, row[0]
            else:
                return False, None
        finally:
            conn.close()


def get_all_partners() -> list[dict]:
    """
    Retorna una lista de diccionarios con la forma:
    {"id": "p001", "nombre": "Nombre Usuario"}
    usando los datos de la columna `name` de la tabla `users`,
    excluyendo el nombre 'Administrador'.
    """
    with sshtunnel.SSHTunnelForwarder(
        SSH_HOST,
        ssh_username=SSH_USER,
        ssh_password=SSH_PASS,
        remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
        allow_agent=False,
        host_pkey_directories=[],
    ) as tunnel:
        conn = MySQLdb.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=DB_USER,
            passwd=DB_PASS,
            db=DB_NAME,
            charset="utf8mb4",
        )
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM users WHERE name <> 'Administrador'")
            rows = cur.fetchall()  # [(name1,), (name2,), ...]

            partners = []
            for i, row in enumerate(rows, start=1):
                partners.append({
                    "id": f"p{i:03d}",   # genera p001, p002, ...
                    "nombre": row[0]     # el valor de name
                })

            cur.close()
            return partners
        finally:
            conn.close()
