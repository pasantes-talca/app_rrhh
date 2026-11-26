from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed

class LicenciaForm(FlaskForm):
    tipo_licencia_id = SelectField('Tipo de Licencia', coerce=int, validators=[DataRequired()])
    fecha_desde = DateField('Fecha Desde', validators=[DataRequired()])
    fecha_hasta = DateField('Fecha Hasta', validators=[DataRequired()])
    cantidad_dias = IntegerField('Cantidad de Días', validators=[DataRequired()])
    motivo = TextAreaField('Motivo / Observaciones', validators=[Optional()])
    archivo_adjunto = FileField('Adjuntar Comprobante (opcional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Solo se permiten documentos e imágenes.')
    ])
    submit = SubmitField('Solicitar Licencia')

class ResolucionLicenciaForm(FlaskForm):
    estado = SelectField('Resolución', choices=[
        ('Aprobada', 'Aprobar'),
        ('Rechazada', 'Rechazar')
    ], validators=[DataRequired()])
    observacion_rrhh = TextAreaField('Observación Interna (RRHH)', validators=[Optional()])
    submit = SubmitField('Guardar Resolución')
