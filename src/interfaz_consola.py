from demo_completa import ejecutar_demo_completa

class InterfazConsola:
    """
    Menú de texto del sistema.
    Solo llama a SistemaVacunacionFacade.
    """
    def __init__(self, sistema):
        self.sistema = sistema
        self.token_actual = None
        self.rol_actual = None

    def ejecutar(self):
        self.mostrar_credenciales()
        while True:
            self.mostrar_resumen_datos()
            print("\n=== Sistema de Gestión de Vacunación ===")
            print("1. Iniciar sesión (Todos)")
            print("2. Registrar centro (CoordinadorCentro)")
            print("3. Cargar lote de vacunas (CoordinadorCentro)")
            print("4. Consultar stock (CoordinadorCentro)")
            print("5. Consultar disponibilidad (PersonaUsuaria)")
            print("6. Reservar cita (PersonaUsuaria)")
            print("7. Consultar citas del día (Vacunador)")
            print("8. Registrar vacunación (Vacunador)")
            print("9. Ejecutar demo completa (Automático)")
            print("0. Salir")
            opcion = input("Seleccione una opción: ").strip()

            try:
                if opcion == "1": self.iniciar_sesion()
                elif opcion == "2": self.registrar_centro()
                elif opcion == "3": self.cargar_lote()
                elif opcion == "4": self.consultar_stock()
                elif opcion == "5": self.consultar_disponibilidad()
                elif opcion == "6": self.reservar_cita()
                elif opcion == "7": self.consultar_citas_del_dia()
                elif opcion == "8": self.registrar_vacunacion()
                elif opcion == "9": ejecutar_demo_completa(self.sistema)
                elif opcion == "0":
                    print("Fin del programa.")
                    break
                else: print("Opción inválida.")
            except Exception as error:
                print("Error:", error)

    def mostrar_credenciales(self):
        print("\nCredenciales de prueba:")
        print("Persona usuaria:       persona@demo.cl / 1234")
        print("Coordinador de centro: coordinador@demo.cl / 1234")
        print("Vacunador:             vacunador@demo.cl / 1234")

    def mostrar_resumen_datos(self):
        """
        Muestra datos disponibles antes del menú.
        Así la persona sabe qué ID usar al reservar, consultar stock o registrar vacunación.
        """
        print("\n--- Datos disponibles actualmente ---")

        print("Campañas:")
        if not self.sistema.base_datos.campanias:
            print("  Sin campañas.")
        for campania in self.sistema.base_datos.campanias.values():
            print(f"  ID {campania.id_campania}: {campania.nombre} ({campania.estado})")

        print("Centros:")
        if not self.sistema.base_datos.centros:
            print("  Sin centros registrados.")
        for centro in self.sistema.base_datos.centros.values():
            print(f"  ID {centro.id_centro}: {centro.nombre} - {centro.direccion} - capacidad {centro.capacidad_diaria}")

        print("Lotes / stock:")
        if not self.sistema.base_datos.lotes:
            print("  Sin lotes cargados.")
        for lote in self.sistema.base_datos.lotes.values():
            print(f"  ID lote {lote.id_lote}: {lote.nombre_vacuna}, centro ID {lote.id_centro}, stock {lote.stock_disponible}")

        print("Citas:")
        if not self.sistema.base_datos.citas:
            print("  Sin citas reservadas.")
        for cita in self.sistema.base_datos.citas.values():
            print(f"  ID cita {cita.id_cita}: persona {cita.id_persona}, centro {cita.id_centro}, fecha {cita.fecha_hora}, estado {cita.estado}")

        if self.rol_actual:
            print(f"Sesión actual: {self.rol_actual}")
        else:
            print("Sesión actual: no iniciada")

    def exigir_sesion(self):
        if self.token_actual is None:
            raise PermissionError("Primero debe iniciar sesión.")

    def iniciar_sesion(self):
        print("\nPuede usar una de estas cuentas:")
        print("  persona@demo.cl / 1234")
        print("  coordinador@demo.cl / 1234")
        print("  vacunador@demo.cl / 1234")

        sesion = self.sistema.iniciar_sesion(input("Correo: "), input("Contraseña: "))
        self.token_actual = sesion.token
        self.rol_actual = sesion.rol
        print("Sesión iniciada. Rol:", sesion.rol)

    def registrar_centro(self):
        self.exigir_sesion()
        print("\nAcción: registrar un nuevo centro de vacunación.")
        print("Ejemplo: nombre = Centro Norte, dirección = Calle 123, capacidad = 30")
        centro = self.sistema.registrar_centro(
            self.token_actual,
            input("Nombre del centro: "),
            input("Dirección: "),
            int(input("Capacidad diaria: "))
        )
        print("Centro registrado:", centro)

    def cargar_lote(self):
        self.exigir_sesion()
        print("\nAcción: cargar stock de vacunas a un centro.")
        self.mostrar_centros()
        print("Ejemplo: ID centro = 1, vacuna = Influenza, stock = 20")
        lote = self.sistema.cargar_lote(
            self.token_actual,
            int(input("ID centro: ")),
            input("Nombre vacuna: "),
            int(input("Stock: "))
        )
        print("Lote cargado:", lote)

    def consultar_stock(self):
        self.exigir_sesion()
        print("\nAcción: consultar stock de un centro.")
        self.mostrar_centros()
        stock = self.sistema.consultar_stock(self.token_actual, int(input("ID centro: ")))
        self.mostrar_lista(stock)

    def consultar_disponibilidad(self):
        self.exigir_sesion()
        print("\nAcción: buscar horarios disponibles antes de reservar.")
        print("Tipos de búsqueda disponibles:")
        print("  centro   -> ejemplo criterio: UdeC")
        print("  fecha    -> ejemplo criterio: 2026-05-10")
        print("  campania -> ejemplo criterio: Influenza")
        resultados = self.sistema.consultar_disponibilidad(
            self.token_actual,
            input("Tipo: "),
            input("Criterio: ")
        )
        self.mostrar_lista(resultados)

    def reservar_cita(self):
        self.exigir_sesion()
        print("\nAcción: reservar cita para la persona usuaria autenticada.")
        print("Use los IDs que aparecen abajo.")
        self.mostrar_centros()
        self.mostrar_campanias()
        print("Ejemplo: centro = 1, campaña = 1, fecha = 2026-05-10 09:00")
        cita = self.sistema.reservar_cita(
            self.token_actual,
            int(input("ID centro: ")),
            int(input("ID campaña: ")),
            input("Fecha y hora, ejemplo 2026-05-10 09:00: ")
        )
        print("Cita reservada:", cita)

    def consultar_citas_del_dia(self):
        self.exigir_sesion()
        print("\nAcción: consultar citas programadas para una fecha.")
        print("Ejemplo: 2026-05-10")
        citas = self.sistema.consultar_citas_del_dia(self.token_actual, input("Fecha: "))
        self.mostrar_lista(citas)

    def registrar_vacunacion(self):
        self.exigir_sesion()
        print("\nAcción: registrar vacunación realizada.")
        print("Primero debe existir una cita. Puede crear una con la opción 6 o ejecutar la demo.")
        self.mostrar_citas()
        self.mostrar_lotes()
        vacunacion = self.sistema.registrar_vacunacion(
            self.token_actual,
            int(input("ID cita: ")),
            int(input("ID lote: ")),
            input("Observaciones: ")
        )
        print("Vacunación registrada:", vacunacion)

    def mostrar_centros(self):
        print("\nCentros disponibles:")
        if not self.sistema.base_datos.centros:
            print("  Sin centros registrados.")
        for centro in self.sistema.base_datos.centros.values():
            print(f"  ID {centro.id_centro}: {centro.nombre}")

    def mostrar_campanias(self):
        print("\nCampañas disponibles:")
        if not self.sistema.base_datos.campanias:
            print("  Sin campañas registradas.")
        for campania in self.sistema.base_datos.campanias.values():
            print(f"  ID {campania.id_campania}: {campania.nombre}")

    def mostrar_lotes(self):
        print("\nLotes disponibles:")
        if not self.sistema.base_datos.lotes:
            print("  Sin lotes cargados.")
        for lote in self.sistema.base_datos.lotes.values():
            print(f"  ID lote {lote.id_lote}: vacuna {lote.nombre_vacuna}, centro {lote.id_centro}, stock {lote.stock_disponible}")

    def mostrar_citas(self):
        print("\nCitas disponibles:")
        if not self.sistema.base_datos.citas:
            print("  Sin citas registradas.")
        for cita in self.sistema.base_datos.citas.values():
            print(f"  ID cita {cita.id_cita}: centro {cita.id_centro}, fecha {cita.fecha_hora}, estado {cita.estado}")

    def mostrar_lista(self, elementos):
        if not elementos:
            print("Sin resultados.")
        for elemento in elementos:
            print("-", elemento)
