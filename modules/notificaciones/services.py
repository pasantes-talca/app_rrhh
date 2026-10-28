import calendar
from datetime import date

from database.models import Empleado, Feriado, Notificacion, Rol, Usuario
from extensions import db
from sqlalchemy import and_, extract, or_


CALENDARIO_MENDOZA_2026 = (
    (date(2026, 1, 1), 'Año Nuevo'),
    (date(2026, 2, 16), 'Carnaval'),
    (date(2026, 2, 17), 'Carnaval'),
    (date(2026, 3, 23), 'Día no laborable con fines turísticos'),
    (date(2026, 3, 24), 'Día Nacional de la Memoria por la Verdad y la Justicia'),
    (date(2026, 4, 2), 'Día del Veterano y de los Caídos en la Guerra de Malvinas'),
    (date(2026, 4, 3), 'Viernes Santo'),
    (date(2026, 5, 1), 'Día del Trabajador'),
    (date(2026, 5, 25), 'Día de la Revolución de Mayo'),
    (date(2026, 6, 15), 'Paso a la Inmortalidad del General Martín Miguel de Güemes'),
    (date(2026, 6, 20), 'Paso a la Inmortalidad del General Manuel Belgrano'),
    (date(2026, 7, 9), 'Día de la Independencia'),
    (date(2026, 7, 10), 'Día no laborable con fines turísticos'),
    (date(2026, 7, 25), 'Día del Santo Patrono Santiago, feriado provincial de Mendoza'),
    (date(2026, 8, 17), 'Paso a la Inmortalidad del General José de San Martín'),
    (date(2026, 10, 12), 'Día del Respeto a la Diversidad Cultural'),
    (date(2026, 11, 23), 'Día de la Soberanía Nacional'),
    (date(2026, 12, 7), 'Día no laborable con fines turísticos'),
    (date(2026, 12, 8), 'Día de la Inmaculada Concepción de María'),
    (date(2026, 12, 25), 'Navidad'),
)


def sincronizar_calendario_mendoza_2026():
    """Carga el calendario oficial sin modificar fechas ya personalizadas por RR. HH."""
    fechas_existentes = {item.fecha for item in Feriado.query.filter(
        Feriado.fecha.between(date(2026, 1, 1), date(2026, 12, 31))
    ).all()}
    nuevas = [Feriado(fecha=fecha, descripcion=descripcion)
              for fecha, descripcion in CALENDARIO_MENDOZA_2026
              if fecha not in fechas_existentes]
    if nuevas:
        db.session.add_all(nuevas)
        db.session.commit()
    return len(nuevas)


def notificar_usuario(usuario_id, titulo, mensaje, tipo, referencia_tipo, referencia_id):
    if not usuario_id:
        return False
    existente = Notificacion.query.filter_by(
        usuario_id=usuario_id,
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id,
    ).first()
    if existente:
        return False
    db.session.add(Notificacion(
        usuario_id=usuario_id, titulo=titulo, mensaje=mensaje, tipo=tipo,
        referencia_tipo=referencia_tipo, referencia_id=referencia_id,
    ))
    return True


def notificar_empleado(empleado_id, titulo, mensaje, tipo, referencia_tipo, referencia_id):
    usuarios = Usuario.query.filter_by(empleado_id=empleado_id, activo=True).all()
    return sum(notificar_usuario(u.id, titulo, mensaje, tipo, referencia_tipo, referencia_id) for u in usuarios)


def notificar_rrhh(titulo, mensaje, tipo, referencia_tipo, referencia_id, excluir_usuario_id=None):
    usuarios = Usuario.query.join(Rol).filter(
        Usuario.activo.is_(True), Rol.nombre.in_(['administrador', 'recursos_humanos'])
    ).all()
    return sum(
        notificar_usuario(u.id, titulo, mensaje, tipo, referencia_tipo, referencia_id)
        for u in usuarios if u.id != excluir_usuario_id
    )


def notificar_noticia(noticia, excluir_usuario_id=None):
    query = Usuario.query.filter(Usuario.activo.is_(True))
    if not noticia.visible_todos:
        condiciones = []
        if noticia.empresa_id:
            condiciones.append(Empleado.empresa_id == noticia.empresa_id)
        if noticia.sector_id:
            condiciones.append(Empleado.sector_id == noticia.sector_id)
        if not condiciones:
            return 0
        query = query.join(Empleado, Usuario.empleado_id == Empleado.id).filter(or_(*condiciones))
    mensaje = noticia.contenido.strip().replace('\n', ' ')
    if len(mensaje) > 180:
        mensaje = mensaje[:177] + '...'
    return sum(
        notificar_usuario(u.id, noticia.titulo, mensaje, 'noticia', 'noticia', noticia.id)
        for u in query.all() if u.id != excluir_usuario_id
    )


def es_cumpleanos_hoy(fecha_nacimiento, hoy=None):
    if not fecha_nacimiento:
        return False
    hoy = hoy or date.today()
    if (fecha_nacimiento.month, fecha_nacimiento.day) == (hoy.month, hoy.day):
        return True
    return (
        fecha_nacimiento.month == 2 and fecha_nacimiento.day == 29
        and hoy.month == 2 and hoy.day == 28 and not calendar.isleap(hoy.year)
    )


def generar_notificaciones_cumpleanos(hoy=None):
    hoy = hoy or date.today()
    condiciones = [
        and_(extract('month', Empleado.fecha_nacimiento) == hoy.month,
             extract('day', Empleado.fecha_nacimiento) == hoy.day)
    ]
    if hoy.month == 2 and hoy.day == 28 and not calendar.isleap(hoy.year):
        condiciones.append(and_(extract('month', Empleado.fecha_nacimiento) == 2,
                                extract('day', Empleado.fecha_nacimiento) == 29))
    empleados = Empleado.query.filter(Empleado.estado == 'Activo', or_(*condiciones)).all()
    creadas = 0
    for empleado in empleados:
        for usuario in Usuario.query.filter_by(empleado_id=empleado.id, activo=True).all():
            creadas += notificar_usuario(
                usuario.id,
                '¡Feliz cumpleaños!',
                f'¡Feliz cumpleaños, {empleado.nombre_apellido}! Todo el equipo de Talca te desea un excelente día.',
                'cumpleanos', f'cumpleanos_{hoy.year}', empleado.id,
            )
    if creadas:
        db.session.commit()
    return creadas


def generar_notificaciones_fechas_importantes(hoy=None):
    """Crea una sola notificación por usuario para cada fecha importante del día."""
    hoy = hoy or date.today()
    fechas = Feriado.query.filter_by(fecha=hoy).all()
    if not fechas:
        return 0
    usuarios = Usuario.query.filter_by(activo=True).all()
    creadas = 0
    for fecha_importante in fechas:
        for usuario in usuarios:
            creadas += notificar_usuario(
                usuario.id, 'Fecha importante', fecha_importante.descripcion,
                'fecha_importante', f'fecha_importante_{hoy.year}', fecha_importante.id,
            )
    if creadas:
        db.session.commit()
    return creadas
