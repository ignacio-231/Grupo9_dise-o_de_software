class EstrategiaBusquedaDisponibilidad:
    """
    PATRÓN DE COMPORTAMIENTO: Strategy.
    Define una forma común para buscar disponibilidad.
    """
    def buscar(self, base_datos, criterio: str):
        raise NotImplementedError

class BusquedaPorCentro(EstrategiaBusquedaDisponibilidad):
    def buscar(self, base_datos, criterio: str):
        return [
            f"Centro ID {c.id_centro} - {c.nombre}: horarios disponibles 09:00, 10:00, 11:00"
            for c in base_datos.centros.values()
            if criterio.lower() in c.nombre.lower()
        ]

class BusquedaPorFecha(EstrategiaBusquedaDisponibilidad):
    def buscar(self, base_datos, criterio: str):
        if not base_datos.centros:
            return []
        return [
            f"{criterio}: Centro ID {c.id_centro} - {c.nombre} disponible a las 09:00"
            for c in base_datos.centros.values()
        ]

class BusquedaPorCampania(EstrategiaBusquedaDisponibilidad):
    def buscar(self, base_datos, criterio: str):
        resultados = []
        for campania in base_datos.campanias.values():
            if criterio.lower() in campania.nombre.lower():
                for centro in base_datos.centros.values():
                    resultados.append(
                        f"Campaña ID {campania.id_campania} - {campania.nombre} en Centro ID {centro.id_centro} - {centro.nombre}: disponible a las 09:00"
                    )
        return resultados
