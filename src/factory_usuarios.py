from modelos import PersonaUsuaria, CoordinadorCentro, Vacunador
from seguridad import Rol

class UsuarioFactory:
    """
    PATRÓN CREACIONAL: Factory / Simple Factory.

    Crea usuarios según rol y evita que la interfaz cree clases concretas.
    """
    @staticmethod
    def crear_usuario(rol: str, datos: dict):
        # Mensaje del UML: crearUsuario(rol, datos): Usuario
        if rol == Rol.PERSONA_USUARIA:
            return PersonaUsuaria(datos["id_usuario"], datos["correo"], datos["password"], rol, datos["rut"], datos["nombre"])
        if rol == Rol.COORDINADOR_CENTRO:
            return CoordinadorCentro(datos["id_usuario"], datos["correo"], datos["password"], rol, datos["nombre"])
        if rol == Rol.VACUNADOR:
            return Vacunador(datos["id_usuario"], datos["correo"], datos["password"], rol, datos["nombre"], datos["registro_funcionario"])
        raise ValueError("Rol no válido.")
