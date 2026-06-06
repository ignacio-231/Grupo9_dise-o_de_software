def ejecutar_demo_completa(sistema):
    """
    Demo del proceso completo:
    coordinador administra centro/stock,
    persona usuaria reserva,
    vacunador registra vacunación.
    """
    print("\n--- DEMO COMPLETA ---")

    print("\n1) Coordinador inicia sesión")
    sesion_coordinador = sistema.iniciar_sesion("coordinador@demo.cl", "1234")
    print("Sesión iniciada como CoordinadorCentro")

    centro = sistema.registrar_centro(sesion_coordinador.token, "Centro Demo Nuevo", "Av. Demo 999", 25)
    print("2) Centro registrado:", centro)

    lote = sistema.cargar_lote(sesion_coordinador.token, centro.id_centro, "Influenza", 10)
    print("3) Lote cargado:", lote)

    stock = sistema.consultar_stock(sesion_coordinador.token, centro.id_centro)
    print("4) Stock consultado:", stock)

    sesion_persona = sistema.iniciar_sesion("persona@demo.cl", "1234")
    disponibilidad = sistema.consultar_disponibilidad(sesion_persona.token, "centro", "Demo")
    print("5) Disponibilidad:", disponibilidad)

    cita = sistema.reservar_cita(sesion_persona.token, centro.id_centro, 1, "2026-05-10 09:00")
    print("6) Cita reservada:", cita)

    sesion_vacunador = sistema.iniciar_sesion("vacunador@demo.cl", "1234")
    citas = sistema.consultar_citas_del_dia(sesion_vacunador.token, "2026-05-10")
    print("7) Citas del día:", citas)

    vacunacion = sistema.registrar_vacunacion(sesion_vacunador.token, cita.id_cita, lote.id_lote, "Sin observaciones.")
    print("8) Vacunación registrada:", vacunacion)

    print("Consulta 1) Cita final:", sistema.base_datos.citas[cita.id_cita])
    print("Consulta 2) Lote final:", sistema.base_datos.lotes[lote.id_lote])
    print("--- FIN DEMO ---")
