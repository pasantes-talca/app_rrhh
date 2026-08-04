import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from database.models import HorasExtra, Empleado
from .forms import UploadVoetimeForm, HorasExtraManualForm

horas_extra_bp = Blueprint('horas_extra', __name__, url_prefix='/horas_extra')

def check_admin_or_rrhh():
    return current_user.rol.nombre in ['administrador', 'recursos_humanos']

@horas_extra_bp.route('/')
@login_required
def index():
    if check_admin_or_rrhh():
        registros = HorasExtra.query.order_by(HorasExtra.fecha.desc()).all()
    else:
        registros = HorasExtra.query.filter_by(empleado_id=current_user.empleado_id).order_by(HorasExtra.fecha.desc()).all()
    pendientes_manuales = sum(
        1 for registro in registros
        if registro.estado == 'Pendiente'
        and registro.cargador
        and registro.cargador.rol.nombre == 'empleado'
    )
    return render_template(
        'horas_extra/index.html', registros=registros,
        pendientes_manuales=pendientes_manuales,
    )


@horas_extra_bp.route('/cargar', methods=['GET', 'POST'])
@login_required
def cargar_manual():
    if check_admin_or_rrhh():
        flash('La carga manual está destinada a empleados. RR. HH. puede procesar el reporte de Voetime.', 'info')
        return redirect(url_for('horas_extra.index'))
    if not current_user.empleado:
        flash('Tu usuario no tiene una ficha de empleado asociada.', 'danger')
        return redirect(url_for('horas_extra.index'))

    form = HorasExtraManualForm()
    if form.validate_on_submit():
        if form.fecha.data > datetime.now().date():
            form.fecha.errors.append('La fecha no puede ser posterior a hoy.')
        else:
            duplicado = HorasExtra.query.filter_by(
                empleado_id=current_user.empleado.id,
                cargado_por=current_user.id,
                fecha=form.fecha.data,
            ).filter(HorasExtra.estado.in_(['Pendiente', 'Aprobado'])).first()
            if duplicado:
                form.fecha.errors.append('Ya enviaste horas extra para esta fecha.')
            else:
                registro = HorasExtra(
                    empleado_id=current_user.empleado.id,
                    fecha=form.fecha.data,
                    cantidad_horas=form.cantidad_horas.data,
                    motivo=(form.motivo.data or '').strip() or None,
                    sector_id=current_user.empleado.sector_id,
                    estado='Pendiente',
                    cargado_por=current_user.id,
                )
                try:
                    db.session.add(registro)
                    db.session.commit()
                    flash('Tus horas extra fueron enviadas a Recursos Humanos.', 'success')
                    return redirect(url_for('horas_extra.index'))
                except Exception:
                    db.session.rollback()
                    current_app.logger.exception('Error al cargar horas extra manuales')
                    flash('No se pudo enviar la solicitud.', 'danger')
    return render_template(
        'horas_extra/cargar_manual.html', form=form,
        hoy=datetime.now().date().isoformat(),
    )

@horas_extra_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not check_admin_or_rrhh():
        flash('No tienes permisos para subir reportes de Voetime.', 'danger')
        return redirect(url_for('horas_extra.index'))

    form = UploadVoetimeForm()
    if form.validate_on_submit():
        f = form.archivo_voetime.data
        filename = secure_filename(f.filename)
        upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'voetime')
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
        f.save(file_path)

        try:
            # Parsear el archivo Excel/HTML
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')
                except Exception:
                    try:
                        df = pd.read_excel(file_path, engine='xlrd')
                    except Exception:
                        # Es un HTML exportado de Voetime, usar BeautifulSoup nativo
                        with open(file_path, 'r', encoding='latin1') as f:
                            html_content = f.read().replace('\x00', '')
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        tabla = soup.find('table')
                        if tabla:
                            count = 0
                            for fila in tabla.find_all('tr')[1:]:
                                celdas = [td.get_text(strip=True) for td in fila.find_all('td')]
                                if len(celdas) < 10:
                                    continue
                                    
                                fecha_str = celdas[1].strip()
                                cuit_val = celdas[2].strip()
                                entrada_val = celdas[6].strip().replace('ds', '').strip()
                                salida_val = celdas[7].strip().replace('ds', '').strip()
                                total_hs_val = celdas[9].strip()
                                
                                if not cuit_val or not fecha_str or 'Totales' in cuit_val:
                                    continue
                                    
                                empleado = Empleado.query.filter_by(cuil=cuit_val).first()
                                if not empleado:
                                    # Intentar extraer DNI del CUIT
                                    import re
                                    match = re.search(r'\d{2}-(\d{7,8})-\d', cuit_val)
                                    if match:
                                        dni_val = match.group(1)
                                        empleado = Empleado.query.filter_by(dni=dni_val).first()
                                        
                                if not empleado:
                                    # Intentar buscar por nombre
                                    nombre_val = celdas[3].strip()
                                    if nombre_val:
                                        empleado = Empleado.query.filter(Empleado.nombre_apellido.ilike(f"%{nombre_val}%")).first()
                                        
                                if empleado and entrada_val and entrada_val != 'Pendiente':
                                    cant_horas = 0.0
                                    if total_hs_val:
                                        from .utils import parsear_horas, redondear_horas_extra
                                        hs_totales_decimal = parsear_horas(total_hs_val)
                                        jornada_horas = float(empleado.jornada_horas) if empleado.jornada_horas else 9.0
                                        hs_extra_raw = hs_totales_decimal - jornada_horas
                                        if hs_extra_raw > 0:
                                            cant_horas = redondear_horas_extra(hs_extra_raw)
                                            
                                    try:
                                        fecha_dt = None
                                        for fmt in ('%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d'):
                                            try:
                                                fecha_dt = datetime.strptime(fecha_str, fmt).date()
                                                break
                                            except ValueError:
                                                continue
                                                
                                        if not fecha_dt:
                                            continue
                                            
                                        h_desde = datetime.strptime(entrada_val, '%H:%M').time() if entrada_val else None
                                        h_hasta = datetime.strptime(salida_val, '%H:%M').time() if salida_val else None
                                        
                                        h_ext = HorasExtra(
                                            empleado_id=empleado.id,
                                            fecha=fecha_dt,
                                            hora_desde=h_desde,
                                            hora_hasta=h_hasta,
                                            cantidad_horas=cant_horas,
                                            estado='Pendiente',
                                            cargado_por=current_user.id
                                        )
                                        db.session.add(h_ext)
                                        count += 1
                                    except Exception as e:
                                        print(f"Error parseando fila HTML: {e}")
                            db.session.commit()
                            flash(f'Reporte procesado exitosamente. Se generaron {count} registros de horas extra pendientes de validación.', 'success')
                            return redirect(url_for('horas_extra.index'))
                        else:
                            flash('No se encontro una tabla en el archivo HTML.', 'warning')
                            return redirect(url_for('horas_extra.index'))

            # Si no era HTML y se parseó con Pandas (.csv, .xlsx, .xls)
            columnas_df = [str(c).strip().lower() for c in df.columns]
            df.columns = columnas_df
            count = 0
            if 'cuit' in columnas_df and 'fecha' in columnas_df:
                for index, row in df.iterrows():
                    cuit_val = str(row['cuit']).strip()
                    fecha_val = str(row['fecha']).strip()
                    
                    if not cuit_val or cuit_val == 'nan' or not fecha_val or fecha_val == 'nan' or 'Totales' in str(row.values):
                        continue
                        
                    empleado = Empleado.query.filter_by(cuil=cuit_val).first()
                    if not empleado:
                        # Intentar extraer DNI del CUIT (ej: 20-12345678-9 -> 12345678)
                        import re
                        match = re.search(r'\d{2}-(\d{7,8})-\d', cuit_val)
                        if match:
                            dni_val = match.group(1)
                            empleado = Empleado.query.filter_by(dni=dni_val).first()
                            
                    if not empleado:
                        # Intentar buscar por nombre
                        nombre_val = str(row.get('nombre', '')).strip()
                        if nombre_val:
                            empleado = Empleado.query.filter(Empleado.nombre_apellido.ilike(f"%{nombre_val}%")).first()
                            
                    if empleado:
                        entrada_val = str(row.get('entradas', '')).strip().replace('ds', '').strip()
                        salida_val = str(row.get('salidas', '')).strip().replace('ds', '').strip()
                        
                        if entrada_val and entrada_val != 'nan' and entrada_val != 'Pendiente':
                            total_hs_val = str(row.get('total hs', '')).strip()
                            cant_horas = 0.0
                            
                            if total_hs_val and total_hs_val != 'nan':
                                from .utils import parsear_horas, redondear_horas_extra
                                hs_totales_decimal = parsear_horas(total_hs_val)
                                jornada_horas = float(empleado.jornada_horas) if empleado.jornada_horas else 9.0
                                hs_extra_raw = hs_totales_decimal - jornada_horas
                                if hs_extra_raw > 0:
                                    cant_horas = redondear_horas_extra(hs_extra_raw)
                                    
                            try:
                                fecha_dt = None
                                for fmt in ('%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d'):
                                    try:
                                        fecha_dt = datetime.strptime(fecha_val, fmt).date()
                                        break
                                    except ValueError:
                                        continue
                                if not fecha_dt:
                                    continue
                                    
                                h_desde = datetime.strptime(entrada_val, '%H:%M').time() if entrada_val else None
                                h_hasta = datetime.strptime(salida_val, '%H:%M').time() if salida_val else None
                                
                                h_ext = HorasExtra(
                                    empleado_id=empleado.id,
                                    fecha=fecha_dt,
                                    hora_desde=h_desde,
                                    hora_hasta=h_hasta,
                                    cantidad_horas=cant_horas,
                                    estado='Pendiente',
                                    cargado_por=current_user.id
                                )
                                db.session.add(h_ext)
                                count += 1
                            except Exception as e:
                                print(f"Error parseando fila Pandas: {e}")
                db.session.commit()
                flash(f'Reporte procesado exitosamente. Se generaron {count} registros de horas extra pendientes de validación.', 'success')
            else:
                flash(f'El archivo Excel/CSV no tiene el formato esperado. Columnas: {df.columns.tolist()}', 'warning')

            return redirect(url_for('horas_extra.index'))
        except Exception as e:
            flash(f'Error al procesar el archivo: {str(e)}', 'danger')
            
    return render_template('horas_extra/upload.html', form=form)

@horas_extra_bp.route('/<int:id>/aprobar', methods=['POST'])
@login_required
def aprobar(id):
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('horas_extra.index'))
    
    registro = HorasExtra.query.get_or_404(id)
    registro.estado = 'Aprobado'
    db.session.commit()
    flash('Horas extra aprobadas.', 'success')
    return redirect(url_for('horas_extra.index'))


@horas_extra_bp.route('/<int:id>/rechazar', methods=['POST'])
@login_required
def rechazar(id):
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('horas_extra.index'))
    registro = HorasExtra.query.get_or_404(id)
    registro.estado = 'Rechazado'
    observacion = request.form.get('observacion', '').strip()
    if observacion:
        registro.observaciones = observacion
    db.session.commit()
    flash('Solicitud de horas extra rechazada.', 'success')
    return redirect(url_for('horas_extra.index'))


@horas_extra_bp.route('/eliminar-seleccionados', methods=['POST'])
@login_required
def eliminar_seleccionados():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('horas_extra.index'))

    ids = request.form.getlist('registro_ids')
    ids_validos = []
    for valor in ids:
        try:
            ids_validos.append(int(valor))
        except (TypeError, ValueError):
            continue

    if not ids_validos:
        flash('Seleccioná al menos un registro para eliminar.', 'warning')
        return redirect(url_for('horas_extra.index'))

    try:
        cantidad = HorasExtra.query.filter(HorasExtra.id.in_(ids_validos)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'Se eliminaron {cantidad} registros de horas extra.', 'success')
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar horas extra seleccionadas')
        flash('No se pudieron eliminar los registros seleccionados.', 'danger')
    return redirect(url_for('horas_extra.index'))


@horas_extra_bp.route('/vaciar', methods=['POST'])
@login_required
def vaciar():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('horas_extra.index'))
    if request.form.get('confirmacion') != 'ELIMINAR':
        flash('No se confirmó la eliminación de todos los registros.', 'warning')
        return redirect(url_for('horas_extra.index'))

    try:
        cantidad = HorasExtra.query.delete(synchronize_session=False)
        db.session.commit()
        flash(f'La lista fue limpiada. Se eliminaron {cantidad} registros.', 'success')
    except Exception:
        db.session.rollback()
        current_app.logger.exception('Error al vaciar horas extra')
        flash('No se pudo limpiar la lista de horas extra.', 'danger')
    return redirect(url_for('horas_extra.index'))

@horas_extra_bp.route('/exportar')
@login_required
def exportar():
    if not check_admin_or_rrhh():
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('horas_extra.index'))
        
    # Recuperar registros pendientes o aprobados del ultimo mes (ejemplo basico)
    todos_los_registros = HorasExtra.query.order_by(HorasExtra.fecha.asc()).all()
    registros = [
        registro for registro in todos_los_registros
        if registro.estado != 'Rechazado'
        and (
            not registro.cargador
            or registro.cargador.rol.nombre != 'empleado'
            or registro.estado == 'Aprobado'
        )
    ]
    if not registros:
        flash('No hay registros para exportar.', 'warning')
        return redirect(url_for('horas_extra.index'))

    try:
        import io
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment
        from .utils import obtener_tipo_dia
        from database.models import Feriado, Empresa
        
        feriados_db = Feriado.query.all()
        feriados = set([f.fecha for f in feriados_db])
        
        template_path = os.path.join(current_app.root_path, 'static', 'excel_templates', 'formatosugerido.xlsx')
        if not os.path.exists(template_path):
            flash('Plantilla excel no encontrada en el sistema.', 'danger')
            return redirect(url_for('horas_extra.index'))
            
        wb = load_workbook(template_path)
        ws = wb.active
        
        # Aqui simularemos la generacion (similar a app.py del repositorio externo)
        # Agrupando por empleado
        por_empleado = {}
        fechas_unicas = set()
        
        for r in registros:
            fechas_unicas.add(r.fecha)
            por_empleado.setdefault(r.empleado_id, []).append(r)
            
        # Escribir fechas en la fila 4 (segun template)
        DIA_A_COL = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 5}
        fechas_ordenadas = sorted(list(fechas_unicas))
        for fecha in fechas_ordenadas:
            col = DIA_A_COL.get(fecha.weekday())
            if col:
                ws.cell(row=4, column=col, value=fecha.strftime('%d/%m/%y'))

        fila = 7
        for emp_id, regs in por_empleado.items():
            emp = Empleado.query.get(emp_id)
            if not emp: continue
            
            horas_por_tipo = {'LAV': 0.0, 'SAB': 0.0, 'DOM_FER': 0.0}
            horas_por_columna = {}
            
            for r in regs:
                if not r.cantidad_horas or r.cantidad_horas <= 0: continue
                
                tipo_dia = obtener_tipo_dia(r.fecha, feriados)
                horas_por_tipo[tipo_dia] += float(r.cantidad_horas)
                
                col = DIA_A_COL.get(r.fecha.weekday())
                if tipo_dia == 'DOM_FER':
                    col = 5 if r.fecha.weekday() == 6 else 12
                    
                if col:
                    horas_por_columna[col] = horas_por_columna.get(col, 0) + float(r.cantidad_horas)
                    
            if sum(horas_por_tipo.values()) <= 0:
                continue
                
            ws.cell(row=fila, column=1, value=emp.empresa.nombre if emp.empresa else '').alignment = Alignment(horizontal='center')
            ws.cell(row=fila, column=2, value=emp.sector.nombre if emp.sector else '').alignment = Alignment(horizontal='center')
            ws.cell(row=fila, column=3, value=emp.cuil or emp.dni).alignment = Alignment(horizontal='center')
            ws.cell(row=fila, column=4, value=emp.nombre_apellido).alignment = Alignment(horizontal='left')
            
            for col, h_ext in horas_por_columna.items():
                ws.cell(row=fila, column=col, value=h_ext).alignment = Alignment(horizontal='center')
                
            # Subtotales con tarifas
            empresa = emp.empresa
            t_lav = float(empresa.tarifa_lav) if empresa and empresa.tarifa_lav else 0.0
            t_sab = float(empresa.tarifa_sab) if empresa and empresa.tarifa_sab else 0.0
            t_dom = float(empresa.tarifa_dom_fer) if empresa and empresa.tarifa_dom_fer else 0.0
            
            sub_lav = horas_por_tipo['LAV'] * t_lav
            sub_sab = horas_por_tipo['SAB'] * t_sab
            sub_dom = horas_por_tipo['DOM_FER'] * t_dom
            sub_total = sub_lav + sub_sab + sub_dom
            
            if sub_lav > 0: ws.cell(row=fila, column=13, value=sub_lav).alignment = Alignment(horizontal='right')
            if sub_sab > 0: ws.cell(row=fila, column=14, value=sub_sab).alignment = Alignment(horizontal='right')
            if sub_dom > 0: ws.cell(row=fila, column=15, value=sub_dom).alignment = Alignment(horizontal='right')
            if sub_total > 0:
                ws.cell(row=fila, column=16, value=sub_total).alignment = Alignment(horizontal='right')
                ws.cell(row=fila, column=18, value=sub_total).alignment = Alignment(horizontal='right')
                
            fila += 1
            
        from flask import send_file
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return send_file(output, download_name=f"HorasExtra_{datetime.now().strftime('%Y%m%d')}.xlsx", as_attachment=True)
    except Exception as e:
        flash(f'Error exportando excel: {str(e)}', 'danger')
        return redirect(url_for('horas_extra.index'))
