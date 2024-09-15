from decimal import Decimal
import boto3
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from mangum import Mangum
from typing import List
from datetime import date

# Inicializa FastAPI y seguridad
app = FastAPI()
security = HTTPBearer()

# Configura los orígenes permitidos para CORS
origins = [
    "http://localhost:3000",  
    "http://cargo-express-monitoring.s3-website.us-east-2.amazonaws.com",  
    "https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws",  
]

# Agregar el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Adaptador para Lambda
handler = Mangum(app)

# Configura DynamoDB
dynamodb = boto3.resource('dynamodb')
table_pedidos = dynamodb.Table('Pedidos')
table_users = dynamodb.Table('Usuarios')  # Nueva tabla para almacenar usuarios

# Clave secreta y configuración de token
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Obtiene el secret key desde una variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelo de Usuario
class User(BaseModel):
    username: str
    password: str

# Modelo de Producto
class Producto(BaseModel):
    IdProducto: str
    producto: str
    precio: Decimal

# Modelo de Pedido
class Pedido(BaseModel):
    pedido_id: str
    repartidor: dict
    productos: List[Producto]
    timestamp: str

# Modelo Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Funciones de autenticación y verificación de token
def verify_password(stored_password: str, provided_password: str):
    return stored_password == provided_password

def get_user_from_dynamo(username: str):
    try:
        response = table_users.get_item(Key={'username': username})
        return response.get('Item')
    except Exception as e:
        return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

# Endpoint para generar token
@app.post("/token", response_model=Token)
async def login_for_access_token(user: User):
    db_user = get_user_from_dynamo(user.username)
    if not db_user or not verify_password(db_user["password"], user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint para registrar pedidos en DynamoDB
@app.post("/registrar_pedido_entregado", status_code=200)
async def registrar_pedido_entregado(pedido: Pedido, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verificar el token
        token = credentials.credentials
        verify_token(token)  # Valida correctamente el token

        # Convertir a Decimal los precios de los productos
        for producto in pedido.productos:
            producto.precio = Decimal(str(producto.precio))
        
        # Guardar pedido en DynamoDB
        table_pedidos.put_item(Item=pedido.dict())
        return {"message": "Pedido registrado exitosamente", "pedido": pedido.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido: {str(e)}")

# Endpoint para obtener pedidos desde DynamoDB
@app.get("/pedidos", status_code=200)
async def obtener_pedidos(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        verify_token(token)  # Valida correctamente el token
        
        response = table_pedidos.scan()
        data = response.get('Items', [])
        return {"pedidos": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")

# Endpoint para obtener métricas
@app.get("/metrics", status_code=200)
async def obtener_metricas(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verificar el token
        token = credentials.credentials
        verify_token(token)  # Valida correctamente el token

        # Consultar la tabla de pedidos
        response = table_pedidos.scan()
        pedidos = response.get('Items', [])

        # Calcular el top 3 productos más vendidos
        productos_vendidos = {}
        total_ventas_dia = 0
        total_pedidos = 0

        for pedido in pedidos:
            total_pedidos += 1
            for producto in pedido["productos"]:
                producto_nombre = producto["producto"]
                producto_precio = float(producto["precio"])

                # Acumular el total de ventas
                total_ventas_dia += producto_precio

                if producto_nombre in productos_vendidos:
                    productos_vendidos[producto_nombre] += 1
                else:
                    productos_vendidos[producto_nombre] = 1

        # Obtener el top 3 productos más vendidos
        top_3_productos = sorted(productos_vendidos.items(), key=lambda x: x[1], reverse=True)[:3]

        # Calcular el precio promedio por pedido
        precio_promedio_por_pedido = total_ventas_dia / total_pedidos if total_pedidos > 0 else 0

        # Devolver las métricas calculadas
        return {
            "top_3_productos": top_3_productos,
            "precio_promedio_por_pedido": precio_promedio_por_pedido,
            "acumulado_ventas_dia": total_ventas_dia
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas: {str(e)}")
