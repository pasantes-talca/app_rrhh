from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import BooleanField, DateField, DecimalField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')


class PerfilForm(FlaskForm):
    nombre_apellido = StringField('Nombre y apellido', validators=[DataRequired(), Length(max=150)])
    correo = StringField('Correo electrónico', validators=[Optional(), Email(), Length(max=150)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=50)])
    fecha_nacimiento = DateField('Fecha de nacimiento', validators=[Optional()])
    genero = SelectField('Género', choices=[('', 'Prefiero no indicarlo'), ('Femenino', 'Femenino'), ('Masculino', 'Masculino'), ('No binario', 'No binario'), ('Otro', 'Otro')], validators=[Optional()])
    domicilio = StringField('Domicilio', validators=[Optional(), Length(max=200)])
    provincia = StringField('Provincia', validators=[Optional(), Length(max=100)])
    codigo_postal = StringField('Código postal', validators=[Optional(), Length(max=20)])
    licencia_conducir = StringField('Licencia de conducir', validators=[Optional(), Length(max=100)])
    dni = StringField('DNI', validators=[Optional(), Length(max=20)])
    cuil = StringField('CUIL', validators=[Optional(), Length(max=30)])
    legajo = StringField('Legajo / usuario de acceso', validators=[Optional(), Length(max=50)])
    empresa_id = SelectField('Empresa', coerce=int, validators=[Optional()])
    sector_id = SelectField('Sector', coerce=int, validators=[Optional()])
    puesto_id = SelectField('Puesto', coerce=int, validators=[Optional()])
    supervisor_id = SelectField('Supervisor', coerce=int, validators=[Optional()])
    jornada_id = SelectField('Jornada', coerce=int, validators=[Optional()])
    jornada_horas = DecimalField('Horas de jornada', places=2, validators=[Optional()])
    fecha_ingreso = DateField('Fecha de ingreso', validators=[Optional()])
    estado = SelectField('Estado', choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo'), ('Baja', 'Baja'), ('Licencia', 'Licencia'), ('Suspendido', 'Suspendido')], validators=[Optional()])
    foto = FileField('Foto de perfil', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Usá una imagen JPG, PNG o WEBP.'),
        FileSize(max_size=5 * 1024 * 1024, message='La imagen no puede superar los 5 MB.'),
    ])
    eliminar_foto = BooleanField('Eliminar mi foto actual')
    submit = SubmitField('Guardar cambios')


class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField('Contraseña actual', validators=[DataRequired()])
    password_nueva = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=8, max=128)])
    confirmar_password = PasswordField('Confirmar nueva contraseña', validators=[
        DataRequired(), EqualTo('password_nueva', message='Las contraseñas no coinciden.')
    ])
    submit_password = SubmitField('Cambiar contraseña')
