from modelos import CentroVacunacion, LoteVacuna, Cita, Vacunacion
from strategy_busqueda import BusquedaPorCentro

class ServicioCentros:
    """Lógica de centros y stock."""
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def registrar_centro(self, nombre: str, direccion: str, capacidad_diaria: int):
        centro = CentroVacunacion(self.base_datos.nuevo_id_centro(), nombre, direccion, capacidad_diaria)
        self.base_datos.centros[centro.id_centro] = centro
        return centro

    def cargar_lote(self, id_centro: int, nombre_vacuna: str, stock: int):
        if id_centro not in self.base_datos.centros:
            raise ValueError("El centro no existe.")
        lote = LoteVacuna(self.base_datos.nuevo_id_lote(), id_centro, nombre_vacuna, stock)
        self.base_datos.lotes[lote.id_lote] = lote
        return lote

    def consultar_stock(self, id_centro: int):
        return [l for l in self.base_datos.lotes.values() if l.id_centro == id_centro]

class ServicioCitas:
    """
    Lógica de citas.

    GRASP Creador: crea Cita.
    Strategy: delega la búsqueda de disponibilidad.
    """
    def __init__(self, base_datos):
        self.base_datos = base_datos
        self.estrategia_busqueda = BusquedaPorCentro()

    def cambiar_estrategia_busqueda(self, estrategia):
        self.estrategia_busqueda = estrategia

    def consultar_disponibilidad(self, criterio: str):
        return self.estrategia_busqueda.buscar(self.base_datos, criterio)

    def reservar_cita(self, id_persona: int, id_centro: int, id_campania: int, fecha_hora: str):
        if id_centro not in self.base_datos.centros:
            raise ValueError("El centro no existe.")
        if id_campania not in self.base_datos.campanias:
            raise ValueError("La campaña no existe.")
        cita = Cita(self.base_datos.nuevo_id_cita(), id_persona, id_centro, id_campania, fecha_hora)
        cita.confirmar()
        self.base_datos.citas[cita.id_cita] = cita
        return cita

    def consultar_citas_del_dia(self, fecha: str):
        return [c for c in self.base_datos.citas.values() if c.fecha_hora.startswith(fecha)]

class ServicioVacunaciones:
    """
    Lógica de vacunaciones.

    GRASP Creador: crea Vacunacion.
    """
    def __init__(self, base_datos):
        self.base_datos = base_datos

    def registrar_vacunacion(self, id_cita: int, id_vacunador: int, id_lote: int, observaciones: str):
        if id_cita not in self.base_datos.citas:
            raise ValueError("La cita no existe.")
        if id_lote not in self.base_datos.lotes:
            raise ValueError("El lote no existe.")

        cita = self.base_datos.citas[id_cita]
        lote = self.base_datos.lotes[id_lote]

        if cita.estado == "REALIZADA":
            raise ValueError("La cita ya fue realizada.")

        lote.descontar_dosis()
        cita.marcar_realizada()

        vacunacion = Vacunacion(self.base_datos.nuevo_id_vacunacion(), id_cita, id_vacunador, id_lote, observaciones)
        self.base_datos.vacunaciones[vacunacion.id_vacunacion] = vacunacion
        return vacunacion
