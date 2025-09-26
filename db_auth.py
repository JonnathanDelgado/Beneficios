import MySQLdb
import sshtunnel

# timeouts recomendados por la guía
sshtunnel.SSH_TIMEOUT = 10.0
sshtunnel.TUNNEL_TIMEOUT = 10.0

SSH_HOST = ('ssh.pythonanywhere.com', 22)
SSH_USER = 'GPON2'                 # tu usuario de PythonAnywhere
SSH_PASS = 'z1x2c345'       # tu contraseña de login web en PythonAnywhere

REMOTE_DB_HOST = 'gpon2.mysql.pythonanywhere-services.com'
REMOTE_DB_PORT = 3306

DB_USER = 'GPON2'                  # usuario MySQL (normalmente el mismo alias)
DB_PASS = 'Mug1w@r@noluffy'         # contraseña configurada en pestaña Databases
DB_NAME = 'GPON2$Usuarios'         # con el prefijo usuario$

def verify_login(usuario: str, password: str) -> bool:
    """
    Verifica credenciales contra la tabla `users` en MySQL usando SHA2-256.
    Retorna True si coincide usuario + hash, en caso contrario False.
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
            cur.execute(
                "SELECT 1 FROM users WHERE usuario=%s AND password_hash = SHA2(%s, 256) LIMIT 1",
                (usuario, password)
            )
            ok = cur.fetchone() is not None
            cur.close()
            return ok
        finally:
            conn.close()
