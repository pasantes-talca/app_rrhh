from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional

class NoticiaForm(FlaskForm):
    titulo = StringField('Título de la Noticia', validators=[DataRequired(), Length(max=200)])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    imagen = FileField('Imagen o archivo adjunto', validators=[
        Optional(),
        FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx'],
            'Se permiten imágenes, PDF, Word y Excel.'
        )
    ])
    
    visible_todos = BooleanField('Visible para toda la empresa', default=True)
    es_fecha_importante = BooleanField('Mostrar como fecha importante en el dashboard')
    fecha_importante = DateField('Fecha del evento', validators=[Optional()])
    
    empresa_id = SelectField('Filtrar por Empresa', coerce=int, default=0)
    sector_id = SelectField('Filtrar por Sector', coerce=int, default=0)
    
    submit = SubmitField('Guardar Noticia')
