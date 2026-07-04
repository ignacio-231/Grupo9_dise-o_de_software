from base_datos_memoria import BaseDatosMemoria
from datos_de_prueba import cargar_datos_de_prueba
from facade_sistema import SistemaVacunacionFacade
from interfaz_consola import InterfazConsola

def main():
    base_datos = BaseDatosMemoria()
    cargar_datos_de_prueba(base_datos)

    sistema = SistemaVacunacionFacade(base_datos)
    interfaz = InterfazConsola(sistema)
    interfaz.ejecutar()

if __name__ == "__main__":
    main()
