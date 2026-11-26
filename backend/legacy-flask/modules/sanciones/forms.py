from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SancionForm(FlaskForm):
    empleado_id = SelectField('Empleado', coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo de medida', choices=[
        ('Apercibimiento', 'Apercibimiento'),
        ('Llamado de atención', 'Llamado de atención'),
        ('Suspensión', 'Suspensión'),
        ('Otra', 'Otra medida disciplinaria'),
    ], validators=[DataRequired()])
    fecha = DateField('Fecha de aplicación', validators=[DataRequired()])
    fecha_desde = DateField('Suspensión desde', validators=[Optional()])
    fecha_hasta = DateField('Suspensión hasta', validators=[Optional()])
    cantidad_dias = DecimalField('Días de suspensión', places=2, validators=[Optional(), NumberRange(min=0.5, max=365)])
    motivo = StringField('Motivo', validators=[DataRequired(), Length(max=200)])
    descripcion = TextAreaField('Descripción de los hechos', validators=[Optional(), Length(max=5000)])
    observaciones = TextAreaField('Observaciones internas de RR. HH.', validators=[Optional(), Length(max=5000)])
    archivo = FileField('Documento de respaldo', validators=[FileAllowed(
        ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
        'Solo se permiten PDF, Word o imágenes.',
    )])
    estado = SelectField('Estado', choices=[
        ('Borrador', 'Borrador'),
        ('Notificada', 'Notificada al empleado'),
        ('Archivada', 'Archivada'),
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar medida')

    def validate(self, extra_validators=None):
        valido = super().validate(extra_validators)
        if self.tipo.data == 'Suspensión':
            if not self.fecha_desde.data:
                self.fecha_desde.errors.append('Indicá la fecha de inicio de la suspensión.')
                valido = False
            if not self.fecha_hasta.data:
                self.fecha_hasta.errors.append('Indicá la fecha de finalización de la suspensión.')
                valido = False
            if self.fecha_desde.data and self.fecha_hasta.data and self.fecha_hasta.data < self.fecha_desde.data:
                self.fecha_hasta.errors.append('La fecha final no puede ser anterior a la inicial.')
                valido = False
            if not self.cantidad_dias.data:
                self.cantidad_dias.errors.append('Indicá la cantidad de días de suspensión.')
                valido = False
        return valido
