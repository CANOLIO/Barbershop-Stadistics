# forms.py - Definición de formularios WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email
from models import Servicio  # Importar directamente desde models


class VisitaForm(FlaskForm):
    # Obtener servicios dinámicamente
    servicios = []

    try:
        servicios = [(str(s.id), f"{s.nombre} (${s.precio})")
                     for s in Servicio.query.all()]
    except:
        # Manejar caso cuando la base de datos no está inicializada
        pass

    nombre_cliente = StringField('Nombre del Cliente', validators=[DataRequired()])
    servicio = SelectField('Servicio', choices=servicios, validators=[DataRequired()])
    profesional = StringField('Profesional', validators=[DataRequired()])
    metodo_pago = SelectField('Método de Pago', choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia')
    ], validators=[DataRequired()])
    monto = FloatField('Monto Pagado', validators=[DataRequired()])
    submit = SubmitField('Registrar Visita')


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    telefono = StringField('Teléfono')
    email = StringField('Email', validators=[Email()])
    submit = SubmitField('Registrar Cliente')