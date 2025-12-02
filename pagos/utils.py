import hashlib
import hmac
import requests
from django.conf import settings
from datetime import datetime
import random
import string

class WompiUtils:
    """Utilidades para integración con Wompi"""
    
    BASE_URL_TEST = 'https://sandbox.wompi.co/v1'
    BASE_URL_PROD = 'https://production.wompi.co/v1'
    
    @staticmethod
    def get_base_url():
        """Obtener URL base según ambiente"""
        return WompiUtils.BASE_URL_TEST if settings.WOMPI_ENV == 'TEST' else WompiUtils.BASE_URL_PROD
    
    @staticmethod
    def generar_referencia():
        """Genera una referencia única para la transacción"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"REF_{timestamp}_{random_str}"
    
    @staticmethod
    def generar_firma_integridad(referencia, monto_en_centavos, moneda='COP'):
        """
        Genera la firma de integridad SHA256 usando el INTEGRITY SECRET
        Concatenación: referencia + monto_en_centavos + moneda + integrity_secret
        """
        # IMPORTANTE: Usar INTEGRITY SECRET, no PRIVATE KEY
        integrity_secret = settings.WOMPI_INTEGRITY_SECRET
        
        # Convertir monto a string sin decimales
        monto_str = str(int(monto_en_centavos))
        
        # Concatenar: referencia + monto + moneda + integrity_secret
        cadena = f"{referencia}{monto_str}{moneda}{integrity_secret}"
        
        # Generar SHA256
        firma = hashlib.sha256(cadena.encode('utf-8')).hexdigest()
        
        return firma
    
    @staticmethod
    def verificar_firma_evento(checksum_recibido, evento_json):
        """
        Verifica la firma de un evento webhook usando EVENTS SECRET
        """
        # Extraer propiedades según el evento
        properties = evento_json['signature']['properties']
        timestamp = evento_json['timestamp']
        
        # Construir cadena concatenando valores de las propiedades
        valores = []
        data = evento_json['data']
        
        for prop in properties:
            keys = prop.split('.')
            valor = data
            for key in keys:
                valor = valor[key]
            valores.append(str(valor))
        
        # Agregar timestamp
        valores.append(str(timestamp))
        
        # Agregar events secret
        valores.append(settings.WOMPI_EVENTS_SECRET)
        
        # Concatenar todo
        cadena = ''.join(valores)
        
        # Calcular SHA256
        firma_calculada = hashlib.sha256(cadena.encode('utf-8')).hexdigest().upper()
        
        return firma_calculada == checksum_recibido.upper()
    
    @staticmethod
    def consultar_transaccion(transaction_id):
        """
        Consulta el estado de una transacción en Wompi
        """
        url = f"{WompiUtils.get_base_url()}/transactions/{transaction_id}"
        
        headers = {
            'Authorization': f'Bearer {settings.WOMPI_PUBLIC_KEY}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error consultando transacción: {e}")
            return None