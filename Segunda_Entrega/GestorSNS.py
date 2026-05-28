import boto3
import os
from dotenv import load_dotenv

load_dotenv()

sns_client = boto3.client('sns', region_name='us-east-1')

TOPIC_ARN = 'arn:aws:sns:us-east-1:116983560918:sicei-notificaciones'

def notificar_alumno(nombres: str, apellidos: str, promedio: float):
	asunto = "SICEI - Calificaciones del Alumno"
	mensaje = f"Hola,\n\nDetalles del alumno:\n- Nombre: {nombres} {apellidos}\n- Calificaciones (Promedio): {promedio}\n\nSistema automatizado de AWS."

	try:
		respuesta = sns_client.publish(
			TopicArn=TOPIC_ARN,
			Message=mensaje,
			Subject=asunto
		)
		return respuesta
	except Exception as e:
		print(f"Error al enviar la notificación SNS: {e}")
		return None