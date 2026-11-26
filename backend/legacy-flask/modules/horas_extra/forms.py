from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import DateField, DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length

class UploadVoetimeForm(FlaskForm):
    archivo_voetime = FileField('Reporte Voetime (CSV o Excel)', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xls', 'xlsx'], 'Solo se permiten archivos CSV o Excel.')
    ])
    submit = SubmitField('Subir y Calcular')


class HorasExtraManualForm(FlaskForm):
    fecha = DateField('Día trabajado', validators=[DataRequired()])
    cantidad_horas = DecimalField(
        'Cantidad de horas extra',
        places=2,
        validators=[DataRequired(), NumberRange(min=0.25, max=16)],
    )
    motivo = TextAreaField('Tarea realizada o motivo', validators=[Length(max=500)])
    submit = SubmitField('Enviar a Recursos Humanos')
