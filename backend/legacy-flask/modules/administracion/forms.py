from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class UsuarioAdminForm(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=3, max=100)])
    nombre_mostrar = StringField('Nombre visible', validators=[DataRequired(), Length(max=150)])
    correo = StringField('Correo electrónico', validators=[Optional(), Email(), Length(max=150)])
    empleado_id = SelectField('Empleado asociado', coerce=int, validators=[Optional()])
    rol_id = SelectField('Rol operativo', coerce=int, validators=[DataRequired()])
    password = PasswordField('Contraseña inicial', validators=[Optional()])
    activo = BooleanField('Cuenta activa', default=True)
    submit = SubmitField('Guardar usuario')


class PasswordAdminForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[DataRequired()])
    confirmar = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Restablecer contraseña')


class SeguridadForm(FlaskForm):
    longitud_minima = IntegerField('Longitud mínima de nuevas contraseñas', validators=[DataRequired(), NumberRange(min=8, max=64)])
    duracion_sesion = IntegerField('Duración máxima de sesión (minutos)', validators=[DataRequired(), NumberRange(min=15, max=10080)])
    submit = SubmitField('Guardar configuración')


class RevisionErrorForm(FlaskForm):
    motivo = TextAreaField('Motivo o resolución', validators=[DataRequired(), Length(min=5, max=1000)])
    submit = SubmitField('Marcar como revisado')
