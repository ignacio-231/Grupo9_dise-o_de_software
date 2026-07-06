from flask import Flask, render_template, request, redirect, url_for, session, flash
from base_datos_memoria import BaseDatosMemoria
from datos_de_prueba import cargar_datos_de_prueba
from facade_sistema import SistemaVacunacionFacade
from modelos import Cita, Vacunacion  # <-- CORRECCIÓN: Se agrega Vacunacion aquí

app = Flask(__name__)
app.secret_key = "vacunared_secret_key_provisional"

# Inicialización del sistema
base_datos = BaseDatosMemoria()
cargar_datos_de_prueba(base_datos)
sistema = SistemaVacunacionFacade(base_datos)

# --- DATOS DE VISTA TEMPORALES ---
base_datos.citas[1] = Cita(id_cita=1, id_persona=1, id_centro=1, id_campania=1, fecha_hora="08/07/2026 a las 09:30 hrs", estado="PROGRAMADA")
base_datos.citas[2] = Cita(id_cita=2, id_persona=1, id_centro=1, id_campania=1, fecha_hora="20/06/2026 a las 10:00 hrs", estado="REALIZADA")
# ---------------------------------

@app.route('/')
def vista_login():
    usuarios_demo = list(base_datos.usuarios.values())
    return render_template('login.html', usuarios=usuarios_demo)

@app.route('/login', methods=['POST'])
def procesar_login():
    correo = request.form.get('correo')
    password = request.form.get('password')
    
    if not correo:
        flash("Por favor, seleccione una cuenta de demostración.", "error")
        return redirect(url_for('vista_login'))
        
    try:
        sesion_usuario = sistema.iniciar_sesion(correo, password)
        session['token'] = sesion_usuario.token
        session['rol'] = sesion_usuario.rol
        session['id_usuario'] = sesion_usuario.id_usuario
        
        # ENRUTADOR INTELIGENTE POR ROL
        if sesion_usuario.rol == 'VACUNADOR':
            return redirect(url_for('vista_dashboard_funcionario'))
        else:
            return redirect(url_for('vista_dashboard'))
        
    except PermissionError as err:
        flash(str(err), "error")
        return redirect(url_for('vista_login'))

# ==========================================
# RUTAS DE CIUDADANO
# ==========================================

@app.route('/dashboard')
def vista_dashboard():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
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
            "campania": campania.nombre if campania else "Campaña General",
            "centro": centro.nombre if centro else "Centro no especificado",
            "fecha_hora": proxima_cita_obj.fecha_hora
        }

    return render_template('dashboard.html', 
                           usuario=usuario, 
                           citas_programadas=citas_programadas, 
                           vacunaciones_recibidas=vacunaciones_recibidas,
                           proxima_cita=proxima_cita)

@app.route('/mis-citas')
def vista_mis_citas():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    citas_usuario = [c for c in base_datos.citas.values() if c.id_persona == usuario.id_usuario]
    citas_vista = []
    
    for c in citas_usuario:
        centro = base_datos.centros.get(c.id_centro)
        campania = base_datos.campanias.get(c.id_campania)
        citas_vista.append({
            "id": c.id_cita,
            "campania": campania.nombre if campania else "Campaña General",
            "centro": centro.nombre if centro else "Centro Desconocido",
            "fecha_hora": c.fecha_hora,
            "estado": c.estado
        })
        
    return render_template('mis_citas.html', 
                           usuario=usuario, 
                           citas=citas_vista,
                           campanias=base_datos.campanias.values(),
                           centros=base_datos.centros.values())

@app.route('/historial')
def vista_historial():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    historial_vista = []
    
    for v in base_datos.vacunaciones.values():
        cita = base_datos.citas.get(v.id_cita)
        if cita and cita.id_persona == usuario.id_usuario:
            centro = base_datos.centros.get(cita.id_centro)
            campania = base_datos.campanias.get(cita.id_campania)
            lote = base_datos.lotes.get(v.id_lote)
            
            historial_vista.append({
                "campania": campania.nombre if campania else "N/A",
                "vacuna_lote": f"{lote.nombre_vacuna} - Lote {v.id_lote}" if lote else "Desconocido",
                "centro": centro.nombre if centro else "N/A",
                "fecha": cita.fecha_hora.split(" ")[0],
                "dosis": 1
            })
            
    return render_template('historial.html', usuario=usuario, historial=historial_vista)

@app.route('/perfil')
def vista_perfil():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    return render_template('perfil.html', usuario=usuario)

@app.route('/estado-campana')
def vista_estado_campania():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    
    campanias_vista = []
    
    for campania in base_datos.campanias.values():
        cita_usuario = next((c for c in base_datos.citas.values() if c.id_persona == usuario.id_usuario and c.id_campania == campania.id_campania), None)
        
        datos_campania = {
            "nombre": campania.nombre,
            "estado_usuario": "SIN_AGENDAR"
        }
        
        if cita_usuario:
            datos_campania["estado_usuario"] = cita_usuario.estado
            datos_campania["cita_fecha_hora"] = cita_usuario.fecha_hora
            
            if cita_usuario.estado == "REALIZADA":
                vacunacion = next((v for v in base_datos.vacunaciones.values() if v.id_cita == cita_usuario.id_cita), None)
                if vacunacion:
                    datos_campania["lote"] = f"Lote {vacunacion.id_lote}"
                datos_campania["fecha_realizada"] = cita_usuario.fecha_hora.split(" ")[0]

        campanias_vista.append(datos_campania)
        
    return render_template('estado_campania.html', usuario=usuario, campanias=campanias_vista)

@app.route('/cancelar-cita/<int:id_cita>', methods=['POST'])
def cancelar_cita(id_cita):
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    try:
        if id_cita in base_datos.citas:
            cita = base_datos.citas[id_cita]
            cita.estado = "CANCELADA"
            
            usuario = base_datos.usuarios.get(cita.id_persona)
            centro = base_datos.centros.get(cita.id_centro)
            
            if usuario and centro:
                sistema.servicio_correo.enviar_cancelacion_cita(
                    correo_destino=usuario.correo,
                    nombre_usuario=usuario.nombre,
                    fecha_hora=cita.fecha_hora,
                    centro=centro.nombre
                )
                
    except Exception as e:
        print(f"Error al cancelar o enviar correo: {e}")
        
    # --- REDIRECCIÓN INTELIGENTE ---
    if session.get('rol') == 'VACUNADOR':
        return redirect(url_for('vista_citas_funcionario'))
    return redirect(url_for('vista_mis_citas'))

@app.route('/asignar-cita', methods=['POST'])
def asignar_cita():
    if 'token' not in session:
        return redirect(url_for('vista_login'))
    
    try:
        usuario = sistema.seguridad.obtener_usuario(session['token'])
        id_campania = int(request.form.get('campania'))
        id_centro = int(request.form.get('centro'))
        fecha = request.form.get('fecha')
        horario = request.form.get('horario')
        
        cita_existente = next((c for c in base_datos.citas.values() 
                               if c.id_persona == usuario.id_usuario 
                               and c.id_campania == id_campania 
                               and c.estado in ["PROGRAMADA", "CONFIRMADA"]), None)
        
        if cita_existente:
            flash("Ya tienes una cita activa para esta campaña. Cancélala primero si deseas reagendar.", "error")
            return redirect(url_for('vista_mis_citas'))
        
        fecha_formateada = f"{fecha} a las {horario} hrs"
        sistema.reservar_cita(session['token'], id_centro, id_campania, fecha_formateada)
        
    except Exception as e:
        print(f"Error al asignar la nueva cita: {e}")
        flash("Ocurrió un error al intentar asignar la cita.", "error")
        
    return redirect(url_for('vista_mis_citas'))

# ==========================================
# RUTAS DE FUNCIONARIO
# ==========================================

@app.route('/funcionario/dashboard')
def vista_dashboard_funcionario():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    
    campanias_activas = len(base_datos.campanias)
    citas_programadas = len([c for c in base_datos.citas.values() if c.estado in ["PROGRAMADA", "CONFIRMADA"]])
    vacunaciones_totales = len(base_datos.vacunaciones)
    centros_totales = len(base_datos.centros)
    
    campanias_stats = []
    for campania in base_datos.campanias.values():
        citas_camp = [c for c in base_datos.citas.values() if c.id_campania == campania.id_campania]
        vacs_camp = [v for v in base_datos.vacunaciones.values() if v.id_cita in [c.id_cita for c in citas_camp]]
        
        tipo = getattr(campania, 'vacuna_tipo', 'Vacuna General')
        fin = getattr(campania, 'fecha_fin', '31/12/2026')
        
        campanias_stats.append({
            "nombre": campania.nombre,
            "subtitulo": f"{tipo} · Hasta {fin}",
            "citas": len(citas_camp),
            "vacunados": len(vacs_camp)
        })
        
    return render_template('funcionario_dashboard.html', usuario=usuario, 
                           m_campanias=campanias_activas, m_citas=citas_programadas, 
                           m_vacunas=vacunaciones_totales, m_centros=centros_totales,
                           campanias_stats=campanias_stats)

@app.route('/funcionario/citas')
def vista_citas_funcionario():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
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
                "persona": paciente.nombre if paciente else "Desconocido",
                "campania": campania.nombre if campania else "N/A",
                "centro": centro.nombre if centro else "N/A",
                "fecha": fecha_sola,
                "hora": hora_sola,
                "estado": c.estado
            })
    
    return render_template('funcionario_citas.html', 
                           usuario=usuario, 
                           citas=citas_todas, 
                           campanias=base_datos.campanias.values(),
                           centros=base_datos.centros.values())   

@app.route('/funcionario/asignar-cita', methods=['POST'])
def asignar_cita_funcionario():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    
    try:
        id_campania = int(request.form.get('campania'))
        id_centro = int(request.form.get('centro'))
        fecha = request.form.get('fecha')
        horario = request.form.get('horario')
        
        id_paciente = session['id_usuario']
        
        cita_existente = next((c for c in base_datos.citas.values() 
                               if c.id_persona == id_paciente 
                               and c.id_campania == id_campania 
                               and c.estado in ["PROGRAMADA", "CONFIRMADA"]), None)
        
        if cita_existente:
            flash("Ya tienes una cita activa para esta campaña.", "error")
            return redirect(url_for('vista_citas_funcionario'))
        
        nueva_cita_id = max(base_datos.citas.keys()) + 1 if base_datos.citas else 1
        fecha_formateada = f"{fecha} a las {horario} hrs"
        
        nueva_cita = Cita(
            id_cita=nueva_cita_id,
            id_persona=id_paciente,
            id_centro=id_centro,
            id_campania=id_campania,
            fecha_hora=fecha_formateada,
            estado="PROGRAMADA"
        )
        
        base_datos.citas[nueva_cita_id] = nueva_cita
        flash("Cita agendada exitosamente.", "success")
        
    except Exception as e:
        print(f"Error al asignar: {e}")
        flash("Ocurrió un error inesperado.", "error")
        
    return redirect(url_for('vista_citas_funcionario'))

@app.route('/funcionario/vacunaciones')
def vista_vacunaciones_funcionario():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    registros = []
    
    for v in base_datos.vacunaciones.values():
        cita = base_datos.citas.get(v.id_cita)
        if cita:
            persona = base_datos.usuarios.get(cita.id_persona)
            registros.append({
                "persona": persona.nombre if persona else "Desconocido",
                "campania": base_datos.campanias.get(cita.id_campania).nombre,
                "centro": base_datos.centros.get(cita.id_centro).nombre,
                "fecha": cita.fecha_hora.split(" ")[0],
                "lote": v.id_lote,
                "dosis": 1,
                "aplicada_por": usuario.nombre
            })
            
    citas_pendientes = [c for c in base_datos.citas.values() if c.estado == "PROGRAMADA"]
    
    return render_template('funcionario_vacunaciones.html', 
                           usuario=usuario, 
                           registros=registros, 
                           citas_pendientes=citas_pendientes)

@app.route('/funcionario/registrar-vacunacion', methods=['POST'])
def registrar_vacunacion_func():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    
    try:
        id_cita = int(request.form.get('id_cita'))
        lote = request.form.get('lote')
        
        if id_cita in base_datos.citas:
            cita = base_datos.citas[id_cita]
            cita.estado = "REALIZADA"
            
            nuevo_id_vac = max(base_datos.vacunaciones.keys()) + 1 if base_datos.vacunaciones else 1
            
            base_datos.vacunaciones[nuevo_id_vac] = Vacunacion(
                id_vacunacion=nuevo_id_vac,
                id_cita=id_cita,
                id_lote=lote
            )
            print(f"Éxito: Vacunación {nuevo_id_vac} registrada para la cita {id_cita}.")
            
    except Exception as e:
        print(f"Error al registrar vacunación: {e}")
        
    return redirect(url_for('vista_vacunaciones_funcionario'))

@app.route('/funcionario/perfil')
def vista_perfil_funcionario():
    if 'token' not in session or session.get('rol') != 'VACUNADOR':
        return redirect(url_for('vista_login'))
    usuario = sistema.seguridad.obtener_usuario(session['token'])
    return render_template('funcionario_perfil.html', usuario=usuario)

# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.route('/logout')
def procesar_logout():
    session.clear()
    return redirect(url_for('vista_login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)