from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

class UploadVoetimeForm(FlaskForm):
    archivo_voetime = FileField('Reporte Voetime (CSV o Excel)', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xls', 'xlsx'], 'Solo se permiten archivos CSV o Excel.')
    ])
    submit = SubmitField('Subir y Calcular')
