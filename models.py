# models.py - Definición de modelos de base de datos
from database import db  # Importar desde database.py
from datetime import datetime, timedelta



class Cliente(db.Model):
    """
    Modelo para almacenar información de clientes
    """
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    visitas = db.relationship('Visita', backref='cliente', lazy=True)

    @property
    def ultima_visita(self):
        return Visita.query.filter_by(cliente_id=self.id).order_by(Visita.fecha.desc()).first()

    @property
    def frecuencia_visitas(self):
        # Calcular frecuencia promedio de visitas (días entre visitas)
        visitas = Visita.query.filter_by(cliente_id=self.id).order_by(Visita.fecha).all()
        if len(visitas) < 2:
            return 30  # Valor predeterminado si no hay suficientes visitas

        diferencias = [(visitas[i + 1].fecha - visitas[i].fecha).days
                       for i in range(len(visitas) - 1)]
        return sum(diferencias) / len(diferencias) if diferencias else 30

    @property
    def proxima_visita_estimada(self):
        if self.ultima_visita:
            return self.ultima_visita.fecha + timedelta(days=self.frecuencia_visitas)
        return None

    @property
    def total_visitas(self):
        return Visita.query.filter_by(cliente_id=self.id).count()


class Servicio(db.Model):
    """
    Catálogo de servicios ofrecidos
    """
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    precio = db.Column(db.Float, nullable=False)


class Visita(db.Model):
    """
    Registro de visitas de clientes
    """
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id'), nullable=False)
    profesional = db.Column(db.String(50), nullable=False)
    metodo_pago = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)

    servicio = db.relationship('Servicio')


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    subdomain = db.Column(db.String(50), unique=True)  # ej: mibarberia.tudominio.com
    created_at = db.Column(db.DateTime, default=datetime.utcnow)