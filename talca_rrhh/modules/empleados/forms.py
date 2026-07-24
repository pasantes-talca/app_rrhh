from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Email

class EmpleadoForm(FlaskForm):
    # Datos Personales
    nombre_apellido = StringField('Nombre y Apellido', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired()])
    cuil = StringField('CUIL', validators=[Optional()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[Optional()])
    genero = SelectField('Género', choices=[
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
        ('Prefiere no informar', 'Prefiere no informar')
    ], validators=[Optional()])
    telefono = StringField('Teléfono', validators=[Optional()])
    correo = StringField('Correo Electrónico', validators=[Optional(), Email()])
    domicilio = StringField('Domicilio', validators=[Optional()])
    provincia = StringField('Provincia', validators=[Optional()])
    codigo_postal = StringField('Código Postal', validators=[Optional()])
    licencia_conducir = StringField('Licencia de Conducir', validators=[Optional()])

    # Datos Laborales
    legajo = StringField('Legajo', validators=[Optional()])
    empresa_id = SelectField('Empresa', coerce=int, validators=[Optional()])
    sector_id = SelectField('Sector', coerce=int, validators=[Optional()])
    puesto_id = SelectField('Puesto de Trabajo', coerce=int, validators=[Optional()])
    supervisor_id = SelectField('Supervisor', coerce=int, validators=[Optional()])
    jornada_id = SelectField('Jornada', coerce=int, validators=[Optional()])
    fecha_ingreso = DateField('Fecha de Ingreso', validators=[Optional()])
    estado = SelectField('Estado', choices=[
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Baja', 'Baja'),
        ('Licencia', 'Licencia'),
        ('Suspendido', 'Suspendido')
    ], validators=[Optional()])

    submit = SubmitField('Guardar Empleado')
