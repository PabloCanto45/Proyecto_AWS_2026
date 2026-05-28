import boto3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = "sicei-fotos-perfil-alumnos"
s3_client = boto3.client('s3', region_name='us-east-1')

def subir_foto_perfil(archivo_bytes: bytes, nombre_original: str) -> str:
    extension = nombre_original.split('.')[-1]
    nombre_unico = f"fotos_perfil/{uuid.uuid4()}.{extension}"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=nombre_unico,
        Body=archivo_bytes,
        ContentType=f"image/{extension}"
    )
    
    return nombre_unico

def generar_url_publica(llave_s3: str) -> str:
    if not llave_s3:
        return None #type: ignore
        
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': llave_s3},
        ExpiresIn=3600
    )