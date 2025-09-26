import requests

def consumir_api_plataformaweb(idcliente, Dpto):
    # URL de la API
    url = "http://gpon2.pythonanywhere.com/detalles_cliente_2"

    # Datos a enviar en el cuerpo de la solicitud
    payload = {
        "idcliente": idcliente,
        "Dpto": Dpto
    }

    # Encabezados de la solicitud
    headers = {
        "Content-Type": "application/json"
    }

    # Realizar la solicitud POST
    try:
        response = requests.post(url, json=payload, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            data = response.json()  # Obtener los datos en formato JSON

            # Procesar la respuesta
            if "error" in data:
                print(f"Error en la respuesta de la API: {data['error']}")
                if "detalles" in data:
                    print("Detalles del error:", data["detalles"])
                return None
            else:
                # Retornar los datos recibidos de la API
                return data
        else:
            print(f"Error al hacer la solicitud. Código de estado: {response.status_code}")
            print("Mensaje de error:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("Ocurrió un error al intentar conectarse con la API:", e)
        return None

# Ejemplo de uso
#idcliente = 42131788
#Dpto = "Lima"
#resultado = consumir_api_plataformaweb(idcliente, Dpto)
#print(resultado)

def extraer_datos(data):
    # Inicializar la lista que contendrá los resultados
    resultados = []

    # Iterar sobre los registros de 'datos' en el objeto JSON
    for cliente in data.get('datos', []):
        # Extraer la lista de servicios si existe
        servicios = cliente.get("servicios", [])
        # Obtener el valor de 'instalado' del primer servicio si existe, de lo contrario vacío
        instalado = servicios[0].get("instalado", "") if servicios else ""

        # Crear un diccionario con los datos específicos
        cliente_info = {
            "cedula": cliente.get("cedula", ""),
            "estado": cliente.get("estado", ""),
            "nombre": cliente.get("nombre", ""),
            "instalado": instalado
        }

        # Agregar el diccionario al arreglo de resultados
        resultados.append(cliente_info)

    return resultados


# Ejemplo de uso:
#idcliente = 42131788
#Dpto = "Lima"
#data = consumir_api_plataformaweb(idcliente, Dpto)
#resultado = extraer_datos(data)
#print(resultado)

from datetime import datetime

def obtener_cliente_mas_antiguo(resultados):
    # Filtrar los clientes que están activos
    clientes_activos = [cliente for cliente in resultados if cliente['estado'] == 'ACTIVO']
    
    # Si no hay clientes activos, retornar None
    if not clientes_activos:
        return None

    # Inicializar una variable para el cliente con la fecha de instalación más antigua
    cliente_mas_antiguo = clientes_activos[0]
    fecha_antigua = datetime.strptime(cliente_mas_antiguo['instalado'], "%Y-%m-%d") if cliente_mas_antiguo['instalado'] else None

    # Recorrer los clientes activos y buscar la fecha más antigua
    for cliente in clientes_activos[1:]:
        fecha_instalada = datetime.strptime(cliente['instalado'], "%Y-%m-%d") if cliente['instalado'] else None
        if fecha_instalada and (fecha_antigua is None or fecha_instalada < fecha_antigua):
            cliente_mas_antiguo = cliente
            fecha_antigua = fecha_instalada

    return cliente_mas_antiguo

# Ejemplo de uso:
#idcliente = 19321315
#Dpto = "Lima"
#data = consumir_api_plataformaweb(idcliente, Dpto)
#resultado = extraer_datos(data)
#cliente_antiguo = obtener_cliente_mas_antiguo(resultado)
#print(cliente_antiguo)


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def verificar_cliente_3_meses(cliente):
    # Asegurarnos de que el cliente tiene una fecha de instalación
    if not cliente or not cliente['instalado']:
        return False, cliente['nombre'] if cliente else "Desconocido"
    
    # Convertir la fecha de instalación a objeto datetime
    fecha_instalada = datetime.strptime(cliente['instalado'], "%Y-%m-%d")
    
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    
    # Restar 3 meses a la fecha actual
    fecha_limite = fecha_actual - relativedelta(months=3)
    
    # Comparar si la fecha de instalación es anterior a 3 meses respecto a la fecha actual
    if fecha_instalada <= fecha_limite:
        return True, cliente['nombre']
    else:
        return False, cliente['nombre']

# Ejemplo de uso:
#idcliente = '20611943777'
#Dpto = "Lima"
#data = consumir_api_plataformaweb(idcliente, Dpto)
#resultado = extraer_datos(data)
#cliente_antiguo = obtener_cliente_mas_antiguo(resultado)  # Suponiendo que ya obtuviste el cliente más antiguo
#resultado_verificacion = verificar_cliente_3_meses(cliente_antiguo)
#print(resultado_verificacion)  # Retornará True si tiene más de 3 meses, False si no
