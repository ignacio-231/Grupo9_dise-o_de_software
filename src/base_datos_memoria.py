class BaseDatosMemoria:
    """
    Base de datos simulada en memoria.
    Evita usar SQL para que la demo sea simple y ejecutable.
    """
    def __init__(self):
        self.usuarios = {}
        self.centros = {}
        self.campanias = {}
        self.lotes = {}
        self.citas = {}
        self.vacunaciones = {}
        self.siguiente_usuario = 1
        self.siguiente_centro = 1
        self.siguiente_lote = 1
        self.siguiente_cita = 1
        self.siguiente_vacunacion = 1

    def nuevo_id_usuario(self):
        v = self.siguiente_usuario
        self.siguiente_usuario += 1
        return v

    def nuevo_id_centro(self):
        v = self.siguiente_centro
        self.siguiente_centro += 1
        return v

    def nuevo_id_lote(self):
        v = self.siguiente_lote
        self.siguiente_lote += 1
        return v

    def nuevo_id_cita(self):
        v = self.siguiente_cita
        self.siguiente_cita += 1
        return v

    def nuevo_id_vacunacion(self):
        v = self.siguiente_vacunacion
        self.siguiente_vacunacion += 1
        return v
