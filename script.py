import requests
import uuid
import random
import json
import datetime
import time

productos = [
  {
    "IdProducto": "pk0001",
    "producto": "Moneda",
    "precio": 1.00
  },
  {
    "IdProducto": "pk0002",
    "producto": "Estuche para gafas",
    "precio": 8.00
  },
  {
    "IdProducto": "pk0003",
    "producto": "Pequeño espejo de bolsillo",
    "precio": 5.00
  },
  {
    "IdProducto": "pk0004",
    "producto": "Pendrive",
    "precio": 12.00
  },
  {
    "IdProducto": "pk0005",
    "producto": "Tarjeta SIM",
    "precio": 3.00
  },
  {
    "IdProducto": "pk0006",
    "producto": "Adaptador de corriente",
    "precio": 10.00
  },
  {
    "IdProducto": "pk0007",
    "producto": "Tijeras pequeñas",
    "precio": 4.00
  },
  {
    "IdProducto": "pk0008",
    "producto": "Pila de botón",
    "precio": 2.50
  },
  {
    "IdProducto": "pk0009",
    "producto": "Goma de borrar",
    "precio": 0.50
  },
  {
    "IdProducto": "pk0010",
    "producto": "Clip sujetapapeles",
    "precio": 0.20
  }
]

repartidores = [
  {
    "IdRepartidor": 101,
    "Nombre": "María López"
  },
  {
    "IdRepartidor": 102,
    "Nombre": "Carlos García"
  },
  {
    "IdRepartidor": 103,
    "Nombre": "Ana Fernández"
  },
  {
    "IdRepartidor": 104,
    "Nombre": "Juan Martínez"
  },
  {
    "IdRepartidor": 105,
    "Nombre": "Laura Sánchez"
  },
  {
    "IdRepartidor": 106,
    "Nombre": "Pedro Gómez"
  },
  {
    "IdRepartidor": 107,
    "Nombre": "Elena Rodríguez"
  },
  {
    "IdRepartidor": 108,
    "Nombre": "Jorge Pérez"
  },
  {
    "IdRepartidor": 109,
    "Nombre": "Sofía Morales"
  },
  {
    "IdRepartidor": 110,
    "Nombre": "Daniel Castillo"
  }
]

def obtener_token():
    url = "https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws/token"
    payload = {
        "username": "PONER AQUI EL USUARIO",
        "password": "PONER AQUI LA CONTRASENA"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Token obtenido correctamente.")
        return response.json()['access_token']
    else:
        print("Error al obtener el token")
        return None

def registrar_pedido_entregado(pedido_id, repartidor, productos, token):
    url = "https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws/registrar_pedido_entregado"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"  # Usar el token dinámico obtenido
    }
    payload = {
        "pedido_id": pedido_id,
        "repartidor": repartidor,
        "productos": productos,
        "timestamp": str(datetime.datetime.now())
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("### Pedido entregado, registrado exitosamente")
    else:
        print("### Error al registrar el pedido entregado")
        print(f"Status Code: {response.status_code}, Response: {response.text}")


# Obtener el token al inicio
token = obtener_token()

if token:
    while True:
        pedido_id = str(uuid.uuid4())
        repartidor = random.choice(repartidores)
        productos_seleccionados = random.choices(productos, k=random.randint(1, 10))

        registrar_pedido_entregado(pedido_id, repartidor, productos_seleccionados, token)
        time.sleep(5)
else:
    print("No se pudo obtener el token. Verifica las credenciales.")
