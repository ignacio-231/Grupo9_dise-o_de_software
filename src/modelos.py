from dataclasses import dataclass

@dataclass
class Usuario:
    id_usuario: int
    correo: str
    password: str
    rol: str

    def autenticar(self, password_ingresada: str) -> bool:
        return self.password == password_ingresada

@dataclass
class PersonaUsuaria(Usuario):
    rut: str
    nombre: str

@dataclass
class CoordinadorCentro(Usuario):
    nombre: str

@dataclass
class Vacunador(Usuario):
    nombre: str
    registro_funcionario: str

@dataclass
class Campania:
    id_campania: int
    nombre: str
    estado: str

@dataclass
class CentroVacunacion:
    id_centro: int
    nombre: str
    direccion: str
    capacidad_diaria: int

@dataclass
class LoteVacuna:
    id_lote: int
    id_centro: int
    nombre_vacuna: str
    stock_disponible: int

    def descontar_dosis(self) -> None:
        # GRASP Experto en Información: el lote conoce y modifica su stock.
        if self.stock_disponible <= 0:
            raise ValueError("No hay stock disponible.")
        self.stock_disponible -= 1

@dataclass
class Cita:
    id_cita: int
    id_persona: int
    id_centro: int
    id_campania: int
    fecha_hora: str
    estado: str = "PROGRAMADA"

    def confirmar(self) -> None:
        self.estado = "CONFIRMADA"

    def marcar_realizada(self) -> None:
        self.estado = "REALIZADA"

@dataclass
class Vacunacion:
    id_vacunacion: int
    id_cita: int
    id_vacunador: int
    id_lote: int
    observaciones: str
