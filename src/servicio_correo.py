import requests

class ServicioCorreoAPI:
    """
    Servicio para enviar notificaciones consumiendo una API REST externa (Ej: Resend).
    Cumple con el patrón de integración de servicios externos.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Endpoint oficial de la API de Resend
        self.url = "https://api.resend.com/emails"
        

    def enviar_confirmacion_cita(self, correo_destino: str, nombre_usuario: str, fecha_hora: str, centro: str):
        if not self.api_key:
            print("-> [Aviso] API Key no configurada. Saltando notificación.")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": "onboarding@resend.dev", # Correo de prueba que te da Resend
            "to": correo_destino,
            "subject": "Confirmación de Reserva - Sistema de Vacunación",
            "html": (
                f"<p>Hola <strong>{nombre_usuario}</strong>,</p>"
                f"<p>Tu cita ha sido confirmada exitosamente.</p>"
                f"<ul>"
                f"<li><strong>Centro:</strong> {centro}</li>"
                f"<li><strong>Fecha y Hora:</strong> {fecha_hora}</li>"
                f"</ul>"
                f"<p>Por favor asiste con 10 minutos de anticipación.</p>"
            )
        }

        try:
            # Aquí ocurre la "interacción real con la API"
            response = requests.post(self.url, json=payload, headers=headers)
            response.raise_for_status() # Lanza error si el status no es 200 OK
            
            print(f"\n-> [Éxito API] Notificación enviada a {correo_destino} (Status: {response.status_code})")
        
        except requests.exceptions.RequestException as e:
            print(f"\n-> [Error API] Falló la comunicación con el servicio de notificaciones: {e}")