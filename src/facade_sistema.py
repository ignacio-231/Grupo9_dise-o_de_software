from seguridad import GestorSeguridad, Operacion
from servicios import ServicioCentros, ServicioCitas, ServicioVacunaciones
from strategy_busqueda import BusquedaPorCentro, BusquedaPorFecha, BusquedaPorCampania
from servicio_correo import ServicioCorreoAPI

class SistemaVacunacionFacade:
    """
    PATRÓN ESTRUCTURAL: Facade.

    Es la puerta de entrada al sistema.
    La interfaz llama a esta clase, no a todos los servicios internos.
    """
    def __init__(self, base_datos):
        self.base_datos = base_datos
        self.seguridad = GestorSeguridad(base_datos)
        self.centros = ServicioCentros(base_datos)
        self.citas = ServicioCitas(base_datos)
        self.vacunaciones = ServicioVacunaciones(base_datos)
        api_key_notificaciones = "re_T7ngMwpF_PLYNGzNSrgwkNPfV1MNTHUGT" 
        self.servicio_correo = ServicioCorreoAPI(api_key_notificaciones)
        self.citas = ServicioCitas(base_datos, self.servicio_correo)

    def iniciar_sesion(self, correo: str, password: str):
        return self.seguridad.iniciar_sesion(correo, password)

    def registrar_centro(self, token: str, nombre: str, direccion: str, capacidad: int):
        self.seguridad.validar_permiso(token, Operacion.REGISTRAR_CENTRO)
        return self.centros.registrar_centro(nombre, direccion, capacidad)

    def cargar_lote(self, token: str, id_centro: int, nombre_vacuna: str, stock: int):
        self.seguridad.validar_permiso(token, Operacion.CARGAR_LOTE)
        return self.centros.cargar_lote(id_centro, nombre_vacuna, stock)

    def consultar_stock(self, token: str, id_centro: int):
        self.seguridad.validar_permiso(token, Operacion.CONSULTAR_STOCK)
        return self.centros.consultar_stock(id_centro)

    def consultar_disponibilidad(self, token: str, tipo_busqueda: str, criterio: str):
        self.seguridad.validar_permiso(token, Operacion.CONSULTAR_DISPONIBILIDAD)
        if tipo_busqueda == "centro":
            self.citas.cambiar_estrategia_busqueda(BusquedaPorCentro())
        elif tipo_busqueda == "fecha":
            self.citas.cambiar_estrategia_busqueda(BusquedaPorFecha())
        elif tipo_busqueda == "campania":
            self.citas.cambiar_estrategia_busqueda(BusquedaPorCampania())
        else:
            raise ValueError("Tipo inválido. Use centro, fecha o campania.")
        return self.citas.consultar_disponibilidad(criterio)

    def reservar_cita(self, token: str, id_centro: int, id_campania: int, fecha_hora: str):
        usuario = self.seguridad.validar_permiso(token, Operacion.RESERVAR_CITA)
        return self.citas.reservar_cita(usuario.id_usuario, id_centro, id_campania, fecha_hora)

    def consultar_citas_del_dia(self, token: str, fecha: str):
        self.seguridad.validar_permiso(token, Operacion.CONSULTAR_CITAS_DIA)
        return self.citas.consultar_citas_del_dia(fecha)

    def registrar_vacunacion(self, token: str, id_cita: int, id_lote: int, observaciones: str):
        usuario = self.seguridad.validar_permiso(token, Operacion.REGISTRAR_VACUNACION)
        return self.vacunaciones.registrar_vacunacion(id_cita, usuario.id_usuario, id_lote, observaciones)
