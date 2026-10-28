from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import BooleanField, DateField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

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
    foto = FileField('Foto de perfil', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Usá una imagen JPG, PNG o WEBP.'),
        FileSize(max_size=5 * 1024 * 1024, message='La imagen no puede superar los 5 MB.'),
    ])
    eliminar_foto = BooleanField('Eliminar mi foto actual')
    submit = SubmitField('Guardar cambios')
