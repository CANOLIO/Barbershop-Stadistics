# app.py - Punto de entrada principal
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap4
import pandas as pd
from database import db  # Importar desde database.py
import os
from flask import send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barber_mvp.db'
bootstrap = Bootstrap4(app)
db.init_app(app)

# Importar modelos y formularios dentro del contexto
with app.app_context():
    from models import Cliente, Visita, Servicio
    from forms import VisitaForm, ClienteForm

    db.create_all()

    # Insertar servicios básicos si no existen
    if Servicio.query.count() == 0:
        servicios = [
            Servicio(nombre="Corte de pelo", precio=15.00),
            Servicio(nombre="Afeitado", precio=10.00),
            Servicio(nombre="Tinte", precio=25.00),
            Servicio(nombre="Corte y barba", precio=22.00)
        ]
        db.session.bulk_save_objects(servicios)
        db.session.commit()


# Ruta para verificar archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# Ruta de prueba para verificar plantillas
@app.route('/test')
def test_template():
    return render_template('index.html')


# Ruta para listar archivos en templates
@app.route('/debug/templates')
def debug_templates():
    try:
        files = os.listdir('templates')
        return "<br>".join(files)
    except Exception as e:
        return f"Error: {str(e)}<br>Current dir: {os.getcwd()}"


# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------------------------------------------------
# ¡TODAS LAS RUTAS PRINCIPALES DEBEN ESTAR EN ESTE NIVEL!
# -------------------------------------------------------------------

@app.route('/registrar_visita', methods=['GET', 'POST'])
def registrar_visita():
    form = VisitaForm()

    if form.validate_on_submit():
        try:
            # Buscar o crear cliente
            cliente = Cliente.query.filter_by(nombre=form.nombre_cliente.data).first()
            if not cliente:
                cliente = Cliente(nombre=form.nombre_cliente.data)
                db.session.add(cliente)
                db.session.commit()

            # Crear nueva visita
            nueva_visita = Visita(
                cliente_id=cliente.id,
                servicio_id=int(form.servicio.data),
                profesional=form.profesional.data,
                metodo_pago=form.metodo_pago.data,
                monto=form.monto.data
            )

            db.session.add(nueva_visita)
            db.session.commit()
            flash('✅ Visita registrada exitosamente!', 'success')
            return redirect(url_for('registrar_visita'))

        except Exception as e:
            db.session.rollback()
            flash(f'⚠️ Error: {str(e)}', 'danger')

    return render_template('registrar.html', form=form)


@app.route('/reportes')
def reportes():
    # Obtener datos para reportes
    visitas = Visita.query.all()

    if not visitas:
        flash('⚠️ No hay datos para generar reportes', 'warning')
        return redirect(url_for('index'))

    # Convertir a DataFrame para análisis
    datos = pd.DataFrame([{
        'fecha': v.fecha,
        'cliente': v.cliente.nombre,
        'servicio': v.servicio.nombre,
        'profesional': v.profesional,
        'monto': v.monto
    } for v in visitas])

    # Calcular métricas
    servicio_popular = datos['servicio'].mode()[0]
    profesional_popular = datos['profesional'].mode()[0]
    ingresos_totales = datos['monto'].sum()
    clientes_unicos = datos['cliente'].nunique()

    return render_template('reportes.html',
                           servicio_popular=servicio_popular,
                           profesional_popular=profesional_popular,
                           ingresos_totales=ingresos_totales,
                           clientes_unicos=clientes_unicos,
                           datos=datos.to_html(classes='table table-striped'))


@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    # Calcular estadísticas para cada cliente

    return render_template('clientes.html', clientes=clientes)

@app.before_request
def set_tenant_db():
    subdomain = request.host.split('.')[0]
    tenant = Tenant.query.filter_by(subdomain=subdomain).first()
    if tenant:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{tenant.subdomain}.db"
        db.init_app(app)

@app.before_request
def require_login():
    if not current_user.is_authenticated and request.endpoint != 'login':
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)