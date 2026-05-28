import boto3
import uuid
import time
import random
import string
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr

load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
TABLA_SESIONES = 'sesiones-alumnos'

def generar_session_string() -> str:
    return ''.join(random.choices(string.digits, k=128))

def crear_sesion(alumno_id: int) -> dict:
    tabla = dynamodb.Table(TABLA_SESIONES) #type: ignore
    session_id = str(uuid.uuid4())
    session_string = generar_session_string()
    fecha_unix = int(time.time())
    
    item = \
        {
        'id': session_id,
        'fecha': fecha_unix,
        'alumnoId': alumno_id,
        'active': True,
        'sessionString': session_string
        }
    
    tabla.put_item(Item=item)
    return item

def buscar_sesion_por_string(session_string: str) -> dict | None:
	tabla = dynamodb.Table(TABLA_SESIONES) #type: ignore
	
	respuesta = tabla.scan(
		FilterExpression=Attr('sessionString').eq(session_string)
	)
	
	items = respuesta.get('Items', [])
	return items[0] if items else None

def desactivar_sesion_por_id(session_id: str):
    tabla = dynamodb.Table(TABLA_SESIONES) #type: ignore
    tabla.update_item(
        Key={'id': session_id},
        UpdateExpression="SET active = :val",
        ExpressionAttributeValues={':val': False}
    )