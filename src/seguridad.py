from dataclasses import dataclass
from uuid import uuid4

class Rol:
    PERSONA_USUARIA = "PERSONA_USUARIA"
    COORDINADOR_CENTRO = "COORDINADOR_CENTRO"
    VACUNADOR = "VACUNADOR"

class Operacion:
    CONSULTAR_DISPONIBILIDAD = "consultar_disponibilidad"
    RESERVAR_CITA = "reservar_cita"
    REGISTRAR_CENTRO = "registrar_centro"
    CARGAR_LOTE = "cargar_lote"
    CONSULTAR_STOCK = "consultar_stock"
    CONSULTAR_CITAS_DIA = "consultar_citas_dia"
    REGISTRAR_VACUNACION = "registrar_vacunacion"

PERMISOS_POR_ROL = {
    Rol.PERSONA_USUARIA: {
        Operacion.CONSULTAR_DISPONIBILIDAD,
        Operacion.RESERVAR_CITA,
    },
    Rol.COORDINADOR_CENTRO: {
        Operacion.REGISTRAR_CENTRO,
        Operacion.CARGAR_LOTE,
        Operacion.CONSULTAR_STOCK,
    },
    Rol.VACUNADOR: {
        Operacion.CONSULTAR_CITAS_DIA,
        Operacion.REGISTRAR_VACUNACION,
    },
}

@dataclass
class Sesion:
    token: str
    id_usuario: int
    rol: str

class GestorSeguridad:
    """
    Seguridad básica:
    autentica usuarios, crea sesión por token y valida permisos por rol.
    """
    def __init__(self, base_datos):
        self.base_datos = base_datos
        self.sesiones = {}

    def iniciar_sesion(self, correo: str, password: str) -> Sesion:
        for usuario in self.base_datos.usuarios.values():
            if usuario.correo == correo and usuario.autenticar(password):
                sesion = Sesion(str(uuid4()), usuario.id_usuario, usuario.rol)
                self.sesiones[sesion.token] = sesion
                return sesion
        raise PermissionError("Correo o contraseña incorrectos.")

    def obtener_usuario(self, token: str):
        if token not in self.sesiones:
            raise PermissionError("Sesión inválida.")
        return self.base_datos.usuarios[self.sesiones[token].id_usuario]

    def validar_permiso(self, token: str, operacion: str):
        usuario = self.obtener_usuario(token)
        if operacion not in PERMISOS_POR_ROL.get(usuario.rol, set()):
            raise PermissionError(f"Acceso denegado. Rol {usuario.rol} no puede ejecutar {operacion}.")
        return usuario
