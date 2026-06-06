from factory_usuarios import UsuarioFactory
from modelos import Campania, CentroVacunacion, LoteVacuna
from seguridad import Rol

def cargar_datos_de_prueba(base_datos):
    """
    Carga usuarios, campaña, centros y lotes iniciales.
    Así el usuario puede probar el sistema sin partir desde cero.
    """
    usuarios = [
        UsuarioFactory.crear_usuario(Rol.PERSONA_USUARIA, {
            "id_usuario": base_datos.nuevo_id_usuario(),
            "correo": "persona@demo.cl",
            "password": "1234",
            "rut": "11.111.111-1",
            "nombre": "Ana Pérez",
        }),
        UsuarioFactory.crear_usuario(Rol.COORDINADOR_CENTRO, {
            "id_usuario": base_datos.nuevo_id_usuario(),
            "correo": "coordinador@demo.cl",
            "password": "1234",
            "nombre": "Carlos Coordinador",
        }),
        UsuarioFactory.crear_usuario(Rol.VACUNADOR, {
            "id_usuario": base_datos.nuevo_id_usuario(),
            "correo": "vacunador@demo.cl",
            "password": "1234",
            "nombre": "Valentina Vacunadora",
            "registro_funcionario": "VAC-001",
        }),
    ]

    for usuario in usuarios:
        base_datos.usuarios[usuario.id_usuario] = usuario

    base_datos.campanias[1] = Campania(1, "Influenza 2026", "ACTIVA")

    # Centros iniciales para que el menú sea más fácil de probar.
    centro_1 = CentroVacunacion(base_datos.nuevo_id_centro(), "Centro Salud UdeC", "Av. Universidad 123", 50)
    centro_2 = CentroVacunacion(base_datos.nuevo_id_centro(), "CESFAM Central", "Calle Principal 456", 40)
    base_datos.centros[centro_1.id_centro] = centro_1
    base_datos.centros[centro_2.id_centro] = centro_2

    # Lotes iniciales para que se pueda consultar stock sin cargar uno manualmente.
    lote_1 = LoteVacuna(base_datos.nuevo_id_lote(), centro_1.id_centro, "Influenza", 10)
    lote_2 = LoteVacuna(base_datos.nuevo_id_lote(), centro_2.id_centro, "Influenza", 8)
    base_datos.lotes[lote_1.id_lote] = lote_1
    base_datos.lotes[lote_2.id_lote] = lote_2
