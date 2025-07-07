"""
SISTEMA DE GESTIÓN PARA BARBERÍA
Versión: 2.0 
"""

import pandas as pd
import datetime as dt
import os

# =====================
# CONFIGURACIÓN INICIAL
# =====================
ARCHIVO_DATOS = os.path.expanduser("~/Documents/registros_barberia.csv")  # Guarda en Documentos
COLUMNAS = [
    'fecha', 'nombre_cliente', 'servicio', 'profesional',
    'metodo_pago', 'monto', 'frecuencia_visita'
]


# =====================
# FUNCIONES AUXILIARES
# =====================
def inicializar_archivo():
    """Inicializa el archivo CSV si no existe"""
    try:
        if not os.path.exists(ARCHIVO_DATOS):
            df = pd.DataFrame(columns=COLUMNAS)
            df.to_csv(ARCHIVO_DATOS, index=False)
            print(f"Archivo creado en: {ARCHIVO_DATOS}")
    except Exception as e:
        print(f"Error al inicializar archivo: {e}")
        exit(1)


def cargar_datos():
    """Carga los datos del archivo CSV"""
    try:
        if os.path.exists(ARCHIVO_DATOS):
            return pd.read_csv(ARCHIVO_DATOS)
        return pd.DataFrame(columns=COLUMNAS)
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return pd.DataFrame(columns=COLUMNAS)


# =====================
# FUNCIONES PRINCIPALES
# =====================
def registrar_visita():
    """Registra una nueva visita de cliente"""
    datos = cargar_datos()

    try:
        print("\n" + "=" * 40)
        print("REGISTRO DE NUEVA VISITA")
        print("=" * 40)

        fecha_actual = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        nombre = input("Nombre del cliente: ").strip().title()

        # Calcular frecuencia de visita
        if not datos.empty:
            visitas_previas = datos[datos['nombre_cliente'] == nombre].shape[0]
        else:
            visitas_previas = 0
        frecuencia = f"Visita #{visitas_previas + 1}"

        servicio = input("Servicio recibido (ej: Corte, Barba, Tinte): ").strip().title()
        profesional = input("Profesional que atendió: ").strip().title()
        metodo = input("Método de pago (Efectivo/Tarjeta/Transferencia): ").strip().title()
        monto = float(input("Monto pagado: $"))

        nuevo_registro = {
            'fecha': fecha_actual,
            'nombre_cliente': nombre,
            'servicio': servicio,
            'profesional': profesional,
            'metodo_pago': metodo,
            'monto': monto,
            'frecuencia_visita': frecuencia
        }

        datos = pd.concat([datos, pd.DataFrame([nuevo_registro])], ignore_index=True)
        datos.to_csv(ARCHIVO_DATOS, index=False)
        print("\n✅ Visita registrada exitosamente!")

    except ValueError:
        print("\n⚠️ Error: Ingrese un monto válido (ej: 25.50)")
    except Exception as e:
        print(f"\n⚠️ Error inesperado: {e}")


def generar_reporte(periodo='semana'):
    """Genera reporte de ingresos y clientes"""
    datos = cargar_datos()

    try:
        if datos.empty:
            print("\n⚠️ No hay datos para generar el reporte")
            return

        datos['fecha'] = pd.to_datetime(datos['fecha'])
        hoy = dt.datetime.now()

        if periodo == 'semana':
            inicio = hoy - dt.timedelta(days=hoy.weekday())
            filtro = datos['fecha'] >= inicio
            titulo = "SEMANAL"
        else:
            inicio = hoy.replace(day=1)
            filtro = datos['fecha'].dt.month == hoy.month
            titulo = "MENSUAL"

        datos_periodo = datos[filtro]

        if datos_periodo.empty:
            print(f"\n⚠️ No hay datos para el período {titulo}")
            return

        total_ingresos = datos_periodo['monto'].sum()
        clientes_unicos = datos_periodo['nombre_cliente'].nunique()
        servicio_popular = datos_periodo['servicio'].mode()[0]
        profesional_popular = datos_periodo['profesional'].mode()[0]

        print("\n" + "=" * 50)
        print(f"REPORTE {titulo} - {hoy.strftime('%d/%m/%Y')}")
        print("=" * 50)
        print(f"📊 Ingresos totales: ${total_ingresos:,.2f}")
        print(f"👥 Clientes únicos: {clientes_unicos}")
        print(f"✂️ Servicio más popular: {servicio_popular}")
        print(f"👨‍✈️ Profesional más activo: {profesional_popular}")
        print(f"📅 Período: {inicio.strftime('%d/%m/%Y')} - {hoy.strftime('%d/%m/%Y')}")
        print("=" * 50)

    except Exception as e:
        print(f"\n⚠️ Error generando reporte: {e}")


def exportar_excel():
    """Exporta los datos a un archivo Excel"""
    try:
        datos = cargar_datos()
        if datos.empty:
            print("\n⚠️ No hay datos para exportar")
            return

        archivo_excel = os.path.expanduser("~/Documents/reporte_barberia.xlsx")

        with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
            # Hoja de registros completos
            datos.to_excel(writer, sheet_name='Registros', index=False)

            # Hoja de resumen
            resumen = pd.DataFrame({
                'Métrica': ['Ingresos Totales', 'Clientes Únicos', 'Servicio Más Popular', 'Profesional Más Activo'],
                'Valor': [
                    f"${datos['monto'].sum():,.2f}",
                    datos['nombre_cliente'].nunique(),
                    datos['servicio'].mode()[0],
                    datos['profesional'].mode()[0]
                ]
            })
            resumen.to_excel(writer, sheet_name='Resumen', index=False)

        print(f"\n✅ Excel exportado exitosamente a: {archivo_excel}")

    except Exception as e:
        print(f"\n⚠️ Error al exportar a Excel: {e}")


# =====================
# INTERFAZ DE USUARIO
# =====================
def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 50)
    print("✂️ BARBERÍA PREMIUM - SISTEMA DE GESTIÓN ✂️")
    print("=" * 50)
    print("1. Registrar nueva visita")
    print("2. Generar reporte semanal")
    print("3. Generar reporte mensual")
    print("4. Exportar datos a Excel")
    print("5. Salir")
    return input("👉 Seleccione una opción (1-5): ")


# =====================
# EJECUCIÓN PRINCIPAL
# =====================
def main():
    """Función principal del programa"""
    inicializar_archivo()

    while True:
        try:
            opcion = mostrar_menu()

            if opcion == '1':
                registrar_visita()
            elif opcion == '2':
                generar_reporte('semana')
            elif opcion == '3':
                generar_reporte('mes')
            elif opcion == '4':
                exportar_excel()
            elif opcion == '5':
                print("\n¡Gracias por usar el sistema! 👋")
                break
            else:
                print("\n⚠️ Opción inválida. Por favor ingrese un número del 1 al 5.")

        except KeyboardInterrupt:
            print("\n\n⚠️ Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"\n⚠️ Error inesperado: {e}")


if __name__ == "__main__":
    main()
