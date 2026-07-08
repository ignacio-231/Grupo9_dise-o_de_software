from flask import Flask, render_template, request, redirect, url_for, session, flash
from base_datos_memoria import BaseDatosMemoria
from datos_de_prueba import cargar_datos_de_prueba
from facade_sistema import SistemaVacunacionFacade
from modelos import Cita, Vacunacion, Campania, CentroVacunacion, LoteVacuna
from factory_usuarios import UsuarioFactory
from seguridad import Rol

app = Flask(__name__)
app.secret_key = "vacunared_secret_key_provisional"

# Inicialización del sistema
base_datos = BaseDatosMemoria()
cargar_datos_de_prueba(base_datos)
sistema = SistemaVacunacionFacade(base_datos)

# ========================================================
# DATOS DE VISTA TEMPORALES (USANDO TUS CLASES REALES)
# ========================================================

# 1. Usuarios del diseño usando tu Factory
base_datos.usuarios[101] = UsuarioFactory.crear_usuario(Rol.PERSONA_USUARIA, {
    "id_usuario": 101, "correo": "maria@demo.cl", "password": "1234", "rut": "11.111.111-1", "nombre": "María González López"
})
base_datos.usuarios[102] = UsuarioFactory.crear_usuario(Rol.PERSONA_USUARIA, {
    "id_usuario": 102, "correo": "carlos@demo.cl", "password": "1234", "rut": "22.222.222-2", "nombre": "Carlos Muñoz Riquelme"
})
base_datos.usuarios[103] = UsuarioFactory.crear_usuario(Rol.PERSONA_USUARIA, {
    "id_usuario": 103, "correo": "diego@demo.cl", "password": "1234", "rut": "33.333.333-3", "nombre": "Diego Fernández Castro"
})

# 2. Campañas del diseño
camp1 = Campania(101, "COVID-19 Refuerzo Bivalente 2026", "ACTIVA")
camp1.vacuna = "Pfizer BioNTech bivalente"
camp1.poblacion = "4.500.000"
camp1.fecha_inicio = "01/01/2026"
camp1.fecha_fin = "30/06/2026"
base_datos.campanias[101] = camp1

camp2 = Campania(102, "Influenza Invierno 2026", "ACTIVA")
camp2.vacuna = "Fluarix Tetra"
camp2.poblacion = "2.000.000"
camp2.fecha_inicio = "15/03/2026"
camp2.fecha_fin = "31/07/2026"
base_datos.campanias[102] = camp2

camp3 = Campania(103, "Hepatitis B — Funcionarios de Salud", "ACTIVA")
camp3.vacuna = "Engerix-B"
camp3.poblacion = "150.000"
camp3.fecha_inicio = "01/01/2026"
camp3.fecha_fin = "31/12/2026"
base_datos.campanias[103] = camp3

# 3. Centros de Vacunación
base_datos.centros[101] = CentroVacunacion(101, "CESFAM Dr. Arturo Baeza Goñi", "Av. Grecia 3000, Ñuñoa", 50)
base_datos.centros[102] = CentroVacunacion(102, "Hospital San Borja Arriarán", "Santa Rosa 1234, Santiago Centro", 50)
base_datos.centros[103] = CentroVacunacion(103, "CESFAM Carol Urzúa", "Av. Departamental 455, La Florida", 50)

# 4. Lotes de vacunas para el historial
base_datos.lotes[901] = LoteVacuna(901, 102, "Fluarix Tetra", 100)

# 5. Citas del diseño
base_datos.citas[1] = Cita(1, 101, 101, 101, "08/07/2026 a las 09:30 hrs")
base_datos.citas[2] = Cita(2, 102, 102, 102, "03/07/2026 a las 11:00 hrs")
base_datos.citas[2].marcar_realizada()
base_datos.citas[3] = Cita(3, 103, 103, 101, "10/07/2026 a las 14:30 hrs")
base_datos.citas[4] = Cita(4, 101, 102, 102, "20/06/2026 a las 10:00 hrs")
base_datos.citas[4].marcar_realizada()
base_datos.citas[5] = Cita(5, 102, 101, 103, "15/07/2026 a las 15:00 hrs")
base_datos.citas[5].estado = "CANCELADA"

# 6. Vacunación real para el historial
base_datos.vacunaciones[1] = Vacunacion(id_vacunacion=1, id_cita=4, id_vacunador=999, id_lote=901, observaciones="Ninguna")
# ========================================================

@app.route('/')
def vista_login():
    usuarios_demo = list(base_datos.usuarios.values())
    return render_template('login.html', usuarios=usuarios_demo)

@app.route('/login', methods=['POST'])
def procesar_login():
    correo = request.form.get('correo')
    password = request.form.get('password')
    
    if not correo:
        flash("Por favor, ingrese sus credenciales.", "error")
        return redirect(url_for('vista_login'))
        
    try:
        sesion_usuario = sistema.iniciar_sesion(correo, password)
        session['token'] = sesion_usuario.token
        session['rol'] = sesion_usuario.rol
        session['id_usuario'] = sesion_usuario.id_usuario
        rol_str = str(sesion_usuario.rol).split('.')[-1]
        
        if rol_str == 'VACUNADOR':
            return redirect(url_for('vista_dashboard_funcionario'))
        elif rol_str == 'COORDINADOR_CENTRO':
            return redirect(url_for('vista_dashboard_coordinador'))
        else:
            return redirect(url_for('vista_dashboard'))
        
    except PermissionError as err:
        flash(str(err), "error")
        return redirect(url_for('vista_login'))

# ==========================================
# FUNCIÓN COMPARTIDA: CANCELAR CITA
# ==========================================
@app.route('/cancelar-cita/<int:id_cita>', methods=['POST'])
def cancelar_cita(id_cita):
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    try:
        if id_cita in base_datos.citas:
            base_datos.citas[id_cita].estado = "CANCELADA"
    except Exception as e:
        print(f"Error al cancelar: {e}")
        
    rol_str = str(session.get('rol')).split('.')[-1]
    if rol_str == 'VACUNADOR':
        return redirect(url_for('vista_citas_funcionario'))
    elif rol_str == 'COORDINADOR_CENTRO':
        return redirect(url_for('vista_citas_coordinador'))
    return redirect(url_for('vista_mis_citas'))

# ==========================================
# RUTAS DE CIUDADANO
# ==========================================
@app.route('/dashboard')
def vista_dashboard():
    if 'token' not in session: return redirect(url_for('vista_login'))
    try:
        usuario = sistema.seguridad.obtener_usuario(session['token'])
    except PermissionError:
        return redirect(url_for('vista_login'))
    
    citas_usuario = [c for c in base_datos.citas.values() if c.id_persona == usuario.id_usuario]
    citas_programadas = len([c for c in citas_usuario if c.estado in ["PROGRAMADA", "CONFIRMADA"]])
    vacunaciones_recibidas = len([c for c in citas_usuario if c.estado == "REALIZADA"])
    
    proxima_cita_obj = next((c for c in citas_usuario if c.estado == "PROGRAMADA"), None)
    proxima_cita = None
    if proxima_cita_obj:
        centro = base_datos.centros.get(proxima_cita_obj.id_centro)
        campania = base_datos.campanias.get(proxima_cita_obj.id_campania)
        proxima_cita = {
            "campania": getattr(campania, 'nombre', "Campaña General"),
            "centro": getattr(centro, 'nombre', "Centro no especificado"),
            "fecha_hora": proxima_cita_obj.fecha_hora
        }

    return render_template('dashboard.html', usuario=usuario, citas_programadas=citas_programadas, vacunaciones_recibidas=vacunaciones_recibidas, proxima_cita=proxima_cita)

@app.route('/mis-citas')
def vista_mis_citas():
    if 'token' not in session: return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    citas_usuario = [c for c in base_datos.citas.values() if c.id_persona == usuario.id_usuario]
    citas_vista = []
    
    for c in citas_usuario:
        centro = base_datos.centros.get(c.id_centro)
        campania = base_datos.campanias.get(c.id_campania)
        citas_vista.append({
            "id": c.id_cita,
            "campania": getattr(campania, 'nombre', "Campaña General"),
            "centro": getattr(centro, 'nombre', "Centro Desconocido"),
            "fecha_hora": c.fecha_hora,
            "estado": c.estado
        })
    return render_template('mis_citas.html', usuario=usuario, citas=citas_vista, campanias=base_datos.campanias.values(), centros=base_datos.centros.values())

@app.route('/historial')
def vista_historial():
    if 'token' not in session: return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    historial_vista = []
    for v in base_datos.vacunaciones.values():
        cita = base_datos.citas.get(v.id_cita)
        if cita and cita.id_persona == usuario.id_usuario:
            centro = base_datos.centros.get(cita.id_centro)
            campania = base_datos.campanias.get(cita.id_campania)
            lote = base_datos.lotes.get(v.id_lote)
            historial_vista.append({
                "campania": getattr(campania, 'nombre', "N/A"),
                "vacuna_lote": f"{getattr(lote, 'nombre_vacuna', 'Desconocido')} · {v.id_lote}" if lote else "Desconocido",
                "centro": getattr(centro, 'nombre', "N/A"),
                "fecha": cita.fecha_hora.split(" ")[0],
                "dosis": 1
            })
    return render_template('historial.html', usuario=usuario, historial=historial_vista)

@app.route('/perfil')
def vista_perfil():
    if 'token' not in session: return redirect(url_for('vista_login'))
    return render_template('perfil.html', usuario=sistema.seguridad.obtener_usuario(session['token']))

@app.route('/estado-campana')
def vista_estado_campania():
    if 'token' not in session: return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    campanias_vista = []
    
    for campania in base_datos.campanias.values():
        cita_usuario = next((c for c in base_datos.citas.values() if c.id_persona == usuario.id_usuario and getattr(c, 'id_campania', -1) == getattr(campania, 'id_campania', 0)), None)
        datos_campania = {"nombre": getattr(campania, 'nombre', 'N/A'), "estado_usuario": "SIN_AGENDAR"}
        if cita_usuario:
            datos_campania["estado_usuario"] = cita_usuario.estado
            datos_campania["cita_fecha_hora"] = cita_usuario.fecha_hora
            if cita_usuario.estado == "REALIZADA":
                vacunacion = next((v for v in base_datos.vacunaciones.values() if v.id_cita == cita_usuario.id_cita), None)
                if vacunacion: datos_campania["lote"] = f"Lote {vacunacion.id_lote}"
                datos_campania["fecha_realizada"] = cita_usuario.fecha_hora.split(" ")[0]
        campanias_vista.append(datos_campania)
    return render_template('estado_campania.html', usuario=usuario, campanias=campanias_vista)

@app.route('/asignar-cita', methods=['POST'])
def asignar_cita():
    if 'token' not in session: return redirect(url_for('vista_login'))
    try:
        usuario = sistema.seguridad.obtener_usuario(session['token'])
        id_campania = int(request.form.get('campania'))
        id_centro = int(request.form.get('centro'))
        fecha = request.form.get('fecha')
        horario = request.form.get('horario')
        
        cita_existente = next((c for c in base_datos.citas.values() if getattr(c, 'id_persona', -1) == usuario.id_usuario and getattr(c, 'id_campania', -1) == id_campania and getattr(c, 'estado', '') in ["PROGRAMADA", "CONFIRMADA"]), None)
        if cita_existente:
            flash("Ya tienes una cita activa para esta campaña. Cancélala primero si deseas reagendar.", "error")
            return redirect(url_for('vista_mis_citas'))
        
        fecha_formateada = f"{fecha} a las {horario} hrs"
        sistema.reservar_cita(session['token'], id_centro, id_campania, fecha_formateada)
    except Exception as e:
        flash("Ocurrió un error al intentar asignar la cita.", "error")
    return redirect(url_for('vista_mis_citas'))

# ==========================================
# RUTAS DE FUNCIONARIO
# ==========================================
@app.route('/funcionario/dashboard')
def vista_dashboard_funcionario():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    
    campanias_activas = len(base_datos.campanias)
    citas_programadas = len([c for c in base_datos.citas.values() if c.estado in ["PROGRAMADA", "CONFIRMADA"]])
    vacunaciones_totales = len(base_datos.vacunaciones)
    centros_totales = len(base_datos.centros)
    
    campanias_stats = []
    for campania in base_datos.campanias.values():
        citas_camp = [c for c in base_datos.citas.values() if getattr(c, 'id_campania', -1) == getattr(campania, 'id_campania', 0)]
        vacs_camp = [v for v in base_datos.vacunaciones.values() if v.id_cita in [c.id_cita for c in citas_camp]]
        
        tipo = getattr(campania, 'vacuna', 'Vacuna General')
        fin = getattr(campania, 'fecha_fin', '31/12/2026')
        
        campanias_stats.append({
            "nombre": getattr(campania, 'nombre', 'N/A'),
            "subtitulo": f"{tipo} · Hasta {fin}",
            "citas": len(citas_camp),
            "vacunados": len(vacs_camp)
        })
    return render_template('funcionario_dashboard.html', usuario=usuario, m_campanias=campanias_activas, m_citas=citas_programadas, m_vacunas=vacunaciones_totales, m_centros=centros_totales, campanias_stats=campanias_stats)

@app.route('/funcionario/citas')
def vista_citas_funcionario():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR': return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    citas_todas = []
    for c in base_datos.citas.values():
        if c.estado in ["PROGRAMADA", "CONFIRMADA"]:
            paciente = base_datos.usuarios.get(c.id_persona)
            campania = base_datos.campanias.get(c.id_campania)
            centro = base_datos.centros.get(c.id_centro)
            
            partes_fecha = c.fecha_hora.split(" a las ")
            fecha_sola = partes_fecha[0] if len(partes_fecha) > 0 else c.fecha_hora
            hora_sola = partes_fecha[1].replace(" hrs", "") if len(partes_fecha) > 1 else ""

            citas_todas.append({
                "id": c.id_cita,
                "persona": getattr(paciente, 'nombre', "Desconocido"),
                "campania": getattr(campania, 'nombre', "N/A"),
                "centro": getattr(centro, 'nombre', "N/A"),
                "fecha": fecha_sola,
                "hora": hora_sola,
                "estado": c.estado
            })
    return render_template('funcionario_citas.html', usuario=usuario, citas=citas_todas, campanias=base_datos.campanias.values(), centros=base_datos.centros.values())   

@app.route('/funcionario/asignar-cita', methods=['POST'])
def asignar_cita_funcionario():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR': return redirect(url_for('vista_login'))
    try:
        id_campania = int(request.form.get('campania'))
        id_centro = int(request.form.get('centro'))
        fecha = request.form.get('fecha')
        horario = request.form.get('horario')
        id_paciente = session['id_usuario']
        
        cita_existente = next((c for c in base_datos.citas.values() if getattr(c, 'id_persona', -1) == id_paciente and getattr(c, 'id_campania', -1) == id_campania and c.estado in ["PROGRAMADA", "CONFIRMADA"]), None)
        if cita_existente:
            flash("Ya tienes una cita activa para esta campaña.", "error")
            return redirect(url_for('vista_citas_funcionario'))
        
        nueva_cita_id = max(base_datos.citas.keys()) + 1 if base_datos.citas else 1
        fecha_formateada = f"{fecha} a las {horario} hrs"
        nueva_cita = Cita(nueva_cita_id, id_paciente, id_centro, id_campania, fecha_formateada)
        base_datos.citas[nueva_cita_id] = nueva_cita
        flash("Cita agendada exitosamente.", "success")
    except Exception as e:
        flash("Ocurrió un error inesperado.", "error")
    return redirect(url_for('vista_citas_funcionario'))

@app.route('/funcionario/vacunaciones')
def vista_vacunaciones_funcionario():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR': return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    registros = []
    for v in base_datos.vacunaciones.values():
        cita = base_datos.citas.get(v.id_cita)
        if cita:
            persona = base_datos.usuarios.get(cita.id_persona)
            campania = base_datos.campanias.get(cita.id_campania)
            centro = base_datos.centros.get(cita.id_centro)
            registros.append({
                "persona": getattr(persona, 'nombre', "Desconocido"),
                "campania": getattr(campania, 'nombre', 'N/A'),
                "centro": getattr(centro, 'nombre', 'N/A'),
                "fecha": cita.fecha_hora.split(" ")[0],
                "lote": v.id_lote,
                "dosis": 1,
                "aplicada_por": usuario.nombre
            })
    citas_pendientes = [c for c in base_datos.citas.values() if c.estado == "PROGRAMADA"]
    return render_template('funcionario_vacunaciones.html', usuario=usuario, registros=registros, citas_pendientes=citas_pendientes)

@app.route('/funcionario/registrar-vacunacion', methods=['POST'])
def registrar_vacunacion_func():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR': 
        return redirect(url_for('vista_login'))
    
    try:
        id_cita = int(request.form.get('id_cita'))
        lote = int(request.form.get('lote'))
        id_vacunador = session['id_usuario']
        
        if id_cita in base_datos.citas:
            cita = base_datos.citas[id_cita]
            cita.marcar_realizada()
            
            nuevo_id_vac = max(base_datos.vacunaciones.keys()) + 1 if base_datos.vacunaciones else 1
            base_datos.vacunaciones[nuevo_id_vac] = Vacunacion(
                id_vacunacion=nuevo_id_vac, 
                id_cita=id_cita, 
                id_vacunador=id_vacunador, 
                id_lote=lote, 
                observaciones="Registrado por sistema"
            )
            print(f"Éxito: Vacunación {nuevo_id_vac} registrada para la cita {id_cita}.")
            
    except Exception as e:
        print(f"Error al registrar vacunación: {e}")
        
    return redirect(url_for('vista_vacunaciones_funcionario'))

@app.route('/funcionario/perfil')
def vista_perfil_funcionario():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'VACUNADOR': return redirect(url_for('vista_login'))
    return render_template('funcionario_perfil.html', usuario=sistema.seguridad.obtener_usuario(session['token']))

# ==========================================
# RUTAS DE COORDINADOR
# ==========================================
@app.route('/coordinador/dashboard')
def vista_dashboard_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO':
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    campanias_activas = len([c for c in base_datos.campanias.values() if getattr(c, 'estado', '').upper() == 'ACTIVA'])
    citas_programadas = len([c for c in base_datos.citas.values() if c.estado.upper() in ["PROGRAMADA", "CONFIRMADA"]])
    
    avances_campanias = []
    for campania in base_datos.campanias.values():
        if getattr(campania, 'estado', '').upper() == 'ACTIVA':
            citas_camp = [c for c in base_datos.citas.values() if getattr(c, 'id_campania', -1) == getattr(campania, 'id_campania', 0)]
            vacunados = len([v for v in base_datos.vacunaciones.values() if v.id_cita in [c.id_cita for c in citas_camp]])
            poblacion_obj = int(str(getattr(campania, 'poblacion', '100')).replace('.', ''))
            porcentaje = int((vacunados / poblacion_obj) * 100) if poblacion_obj > 0 else 0
            
            avances_campanias.append({
                "nombre": getattr(campania, 'nombre', 'N/A'),
                "subtitulo": f"{getattr(campania, 'vacuna', 'Vacuna General')} · Hasta {getattr(campania, 'fecha_fin', '31/12/2026')}",
                "citas": len(citas_camp),
                "vacunados": vacunados,
                "porcentaje": porcentaje
            })
            
    return render_template('coordinador_dashboard.html', usuario=usuario, kpi_campanias=campanias_activas, kpi_citas=citas_programadas, kpi_vacunaciones=len(base_datos.vacunaciones), kpi_centros=len(base_datos.centros), avances=avances_campanias)

@app.route('/coordinador/campanias')
def vista_campanias_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    campanias_vista = []
    for c in base_datos.campanias.values():
        campanias_vista.append({
            "id_campania": getattr(c, 'id_campania', 0),
            "nombre": getattr(c, 'nombre', 'N/A'),
            "estado": getattr(c, 'estado', 'PROGRAMADA'),
            "vacuna": getattr(c, 'vacuna', 'No especificada'),
            "fecha_inicio": getattr(c, 'fecha_inicio', 'Pendiente'),
            "fecha_fin": getattr(c, 'fecha_fin', 'Pendiente'),
            "descripcion": getattr(c, 'descripcion', ''),
            "poblacion": getattr(c, 'poblacion', '0')
        })
    campanias_vista.reverse()
    return render_template('coordinador_campanias.html', usuario=usuario, campanias=campanias_vista)

@app.route('/coordinador/campanias/nueva', methods=['POST'])
def nueva_campania_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    try:
        nombre = request.form.get('nombre')
        vacuna = request.form.get('vacuna')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        estado = request.form.get('estado')
        descripcion = request.form.get('descripcion')
        poblacion = request.form.get('poblacion')
        
        if fecha_inicio:
            partes = fecha_inicio.split('-')
            fecha_inicio = f"{partes[2]}/{partes[1]}/{partes[0]}"
        if fecha_fin:
            partes = fecha_fin.split('-')
            fecha_fin = f"{partes[2]}/{partes[1]}/{partes[0]}"

        nuevo_id = max(base_datos.campanias.keys()) + 1 if base_datos.campanias else 1
        nueva_campania = Campania(nuevo_id, nombre, estado)
        nueva_campania.vacuna = vacuna
        nueva_campania.fecha_inicio = fecha_inicio
        nueva_campania.fecha_fin = fecha_fin
        nueva_campania.descripcion = descripcion
        if poblacion: nueva_campania.poblacion = f"{int(poblacion):,}".replace(",", ".")
        else: nueva_campania.poblacion = "0"
            
        base_datos.campanias[nuevo_id] = nueva_campania
    except Exception as e:
        print(f"Error al crear campaña: {e}")
    return redirect(url_for('vista_campanias_coordinador'))

@app.route('/coordinador/centros')
def vista_centros_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    centros = list(base_datos.centros.values())
    lotes = list(base_datos.lotes.values())
    personal = [u for u in base_datos.usuarios.values() if str(getattr(u, 'rol', '')).split('.')[-1] == 'VACUNADOR']
    return render_template('coordinador_centros.html', usuario=usuario, centros=centros, lotes=lotes, personal=personal)

@app.route('/coordinador/centros/nuevo', methods=['POST'])
def nuevo_centro_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    try:
        nombre = request.form.get('nombre')
        ubicacion = request.form.get('ubicacion')
        capacidad = request.form.get('capacidad', 50)
        nuevo_id = max(base_datos.centros.keys()) + 1 if base_datos.centros else 1
        nuevo_centro = CentroVacunacion(nuevo_id, nombre, ubicacion, int(capacidad))
        base_datos.centros[nuevo_id] = nuevo_centro
    except Exception as e: pass
    return redirect(url_for('vista_centros_coordinador'))

@app.route('/coordinador/citas')
def vista_citas_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    
    citas_vista = []
    for c in base_datos.citas.values():
        paciente = base_datos.usuarios.get(c.id_persona)
        campania = base_datos.campanias.get(getattr(c, 'id_campania', 0))
        centro = base_datos.centros.get(getattr(c, 'id_centro', 0))
        
        partes_fecha = getattr(c, 'fecha_hora', '').split(" a las ")
        fecha = partes_fecha[0] if len(partes_fecha) > 0 else c.fecha_hora
        hora = partes_fecha[1].replace(" hrs", "") if len(partes_fecha) > 1 else "--:--"
        
        citas_vista.append({
            "id": getattr(c, 'id_cita', 0),
            "persona": getattr(paciente, 'nombre', 'Desconocido'),
            "campania": getattr(campania, 'nombre', 'N/A'),
            "centro": getattr(centro, 'nombre', 'N/A'),
            "fecha": fecha,
            "hora": hora,
            "estado": getattr(c, 'estado', '').lower()
        })
    citas_vista.reverse()
    return render_template('coordinador_citas.html', usuario=usuario, citas=citas_vista, personas=base_datos.usuarios, campanias=base_datos.campanias, centros=base_datos.centros)

@app.route('/coordinador/citas/nueva', methods=['POST'])
def asignar_cita_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    try:
        id_persona = int(request.form.get('persona'))
        id_campania = int(request.form.get('campania'))
        id_centro = int(request.form.get('centro'))
        fecha = request.form.get('fecha')
        horario = request.form.get('horario')
        
        if fecha:
            partes = fecha.split('-')
            fecha_str = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            fecha_str = "Sin fecha"
            
        fecha_formateada = f"{fecha_str} a las {horario} hrs"
        nuevo_id = max(base_datos.citas.keys()) + 1 if base_datos.citas else 1
        
        nueva_cita = Cita(nuevo_id, id_persona, id_centro, id_campania, fecha_formateada)
        base_datos.citas[nuevo_id] = nueva_cita
    except Exception as e:
        print(f"Error al asignar cita desde coordinador: {e}")
    return redirect(url_for('vista_citas_coordinador'))

@app.route('/coordinador/perfil')
def vista_perfil_coordinador():
    if 'token' not in session or str(session.get('rol')).split('.')[-1] != 'COORDINADOR_CENTRO': return redirect(url_for('vista_login'))
    return render_template('coordinador_perfil.html', usuario=sistema.seguridad.obtener_usuario(session['token']))

@app.route('/logout')
def procesar_logout():
    session.clear()
    return redirect(url_for('vista_login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)