from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional, Regexp


FORMATOS_DOCUMENTO = [
    'pdf',
    'doc', 'docx',
    'xls', 'xlsx',
    'ppt', 'pptx',
    'txt',
    'jpg', 'jpeg', 'png', 'gif', 'webp',
]
MENSAJE_FORMATOS = 'Formatos permitidos: PDF, Word, Excel, PowerPoint, TXT e imágenes.'


class DocumentoForm(FlaskForm):
    empleado_id = SelectField('Destino del documento', coerce=int, validators=[Optional()])
    tipo_documento_id = SelectField('Tipo de documento', coerce=int, validators=[DataRequired()])
    nombre_documento = StringField('Nombre o descripción breve', validators=[DataRequired(), Length(max=200)])
    archivo = FileField('Archivo adjunto', validators=[
        FileRequired(),
        FileAllowed(FORMATOS_DOCUMENTO, MENSAJE_FORMATOS),
    ])
    visible_empleado = BooleanField('Compartir este documento con el empleado', default=False)
    observaciones = TextAreaField('Observaciones adicionales')
    submit = SubmitField('Subir documento')


class DocumentoEmpleadoForm(FlaskForm):
    tipo_documento_id = SelectField('Tipo de documento', coerce=int, validators=[DataRequired()])
    nombre_documento = StringField('Nombre o descripción breve', validators=[DataRequired(), Length(max=200)])
    archivo = FileField('Archivo adjunto', validators=[
        FileRequired(),
        FileAllowed(FORMATOS_DOCUMENTO, MENSAJE_FORMATOS),
    ])
    observaciones = TextAreaField('Mensaje para Recursos Humanos')
    submit = SubmitField('Enviar a Recursos Humanos')


class DocumentoEditarForm(FlaskForm):
    empleado_id = SelectField('Destino del documento', coerce=int, validators=[Optional()])
    tipo_documento_id = SelectField('Tipo de documento', coerce=int, validators=[DataRequired()])
    nombre_documento = StringField('Nombre o descripción breve', validators=[DataRequired(), Length(max=200)])
    archivo = FileField('Reemplazar archivo', validators=[
        FileAllowed(FORMATOS_DOCUMENTO, MENSAJE_FORMATOS),
    ])
    visible_empleado = BooleanField('Visible para el empleado')
    observaciones = TextAreaField('Observaciones adicionales')
    submit = SubmitField('Guardar cambios')


class ReciboSueldoForm(FlaskForm):
    empleado_id = SelectField('Empleado', coerce=int, validators=[DataRequired()])
    periodo = StringField('Período', validators=[
        DataRequired(), Regexp(r'^\d{4}-(0[1-9]|1[0-2])$', message='Usá el formato AAAA-MM.'),
    ])
    fecha_limite = DateField('Fecha límite para confirmar', validators=[Optional()])
    archivo = FileField('Recibo en PDF', validators=[
        FileRequired(), FileAllowed(['pdf'], 'El recibo debe ser un archivo PDF.'),
    ])
    observaciones = TextAreaField('Mensaje para el empleado', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Publicar recibo')
