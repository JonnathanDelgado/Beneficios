import os
import gspread
from google.oauth2.service_account import Credentials

def buscar_cliente_por_dni(dni: str):
    """
    Busca un DNI en la columna B del Google Sheet y devuelve info del cliente.
    Retorna None si no lo encuentra.
    """
    # Ruta al JSON en static
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    JSON_PATH = os.path.join(BASE_DIR, "static", "cobertura-cusco-bf6ce6c6518d.json")
    URL = "https://docs.google.com/spreadsheets/d/1TOKQp_ZCn8tE-Mtt7PvE2ims4RI674dHxT6Xt5lkYsM/edit?gid=0#gid=0"
    
    # Autenticación
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(JSON_PATH, scopes=scopes)
    client = gspread.authorize(creds)

    # Abrir hoja
    sh = client.open_by_url(URL)
    ws = sh.sheet1
    values = ws.get_all_values()   # todas las filas

    # Encabezados: asumimos que la primera fila son headers
    headers = values[0]
    rows = values[1:]

    # Recorremos filas buscando en columna B (índice 1)
    for row in rows:
        if row[1].strip() == str(dni).strip():   # columna B
            cliente_info = {
                "cedula": row[1],     # Columna B
                "estado": row[4],     # Columna E
                "nombre": row[2],     # Columna C
                "instalado": row[3]   # Columna D
            }
            return cliente_info

    return None  # No encontrado



#resultado = buscar_cliente_por_dni("76147078")

#if resultado:
    print("Cliente encontrado:", resultado)
#else:
    #print("DNI no encontrado en la hoja.")
