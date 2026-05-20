from io import BytesIO
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from database import obtener_conexion
import random
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

empleados_bp = Blueprint(
    "empleados",
    __name__,
    url_prefix="/empleados"
)

# -----------------------------------
# LOGIN EMPLOY
# -----------------------------------

@empleados_bp.route(
    "/login-employ",
    methods=["GET", "POST"]
)
def login_employ():

    # -----------------------------------
    # GET
    # -----------------------------------

    if request.method == "GET":

        return render_template(
            "empleados-html/login_employ.html"
        )

    # -----------------------------------
    # DATOS
    # -----------------------------------

    id_empleado = request.form["id_empleado"].strip()

    contrasena = request.form["contrasena"].strip()

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # VALIDAR LOGIN
    # -----------------------------------

    cursor.execute(
        """
        SELECT
            empleados.id,
            empleados.id_empleado,
            empleados.cliente_id,
            empleados.contrasena,
            clientes.nombre
        FROM empleados

        INNER JOIN clientes
            ON empleados.cliente_id = clientes.id

        WHERE empleados.id_empleado = %s
        AND empleados.contrasena = %s
        """,
        (
            id_empleado,
            contrasena
        )
    )

    empleado = cursor.fetchone()

    conexion.close()

    if not empleado:

        return render_template(
            "empleados-html/login_employ.html",
            error="Datos incorrectos"
        )

    # -----------------------------------
    # SESION
    # -----------------------------------

    session["empleado_id"] = empleado["id"]

    session["cliente_id"] = empleado["cliente_id"]

    session["id_empleado"] = empleado["id_empleado"]

    session["empleado_nombre"] = empleado["nombre"]

    return redirect(
        url_for("empleados.catalogo_employ")
    )

# -----------------------------------
# LOGOUT EMPLOY
# -----------------------------------

@empleados_bp.route("/logout-employ")
def logout_employ():

    session.pop("empleado_id", None)
    session.pop("cliente_id", None)
    session.pop("id_empleado", None)
    session.pop("empleado_nombre", None)

    return redirect(
        url_for("empleados.login_employ")
    )

# -----------------------------------
# CREAR EMPLOY
# -----------------------------------

@empleados_bp.route(
    "/crear-employ",
    methods=["GET", "POST"]
)
def crear_employ():

    # -----------------------------------
    # GET
    # -----------------------------------

    if request.method == "GET":

        return render_template(
            "empleados-html/crud/crear_employ.html"
        )

    # -----------------------------------
    # DATOS
    # -----------------------------------

    documento = request.form["documento"].strip()

    contrasena = request.form["contrasena"].strip()

    telefono = request.form["telefono"].strip()

    email = request.form["email"].strip()

    pin = request.form["pin"].strip()

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # VALIDAR DOCUMENTO
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE documento = %s
        """,
        (documento,)
    )

    cliente = cursor.fetchone()

    if not cliente:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="El documento no existe"
        )

    # -----------------------------------
    # VALIDAR TELEFONO
    # -----------------------------------

    if telefono != cliente["telefono"]:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="El telefono no existe"
        )

    # -----------------------------------
    # VALIDAR EMAIL
    # -----------------------------------

    if email != cliente["email"]:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="El Email no existe"
        )

    # -----------------------------------
    # VALIDAR PIN
    # -----------------------------------

    if not pin:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="El PIN no puede estar vacio"
        )

    if not pin.isdigit():

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="El PIN solo debe contener numeros"
        )

    if pin != cliente["pin"]:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="PIN incorrecto"
        )

    # -----------------------------------
    # VALIDAR CONTRASENA
    # -----------------------------------

    if len(contrasena) < 4 or len(contrasena) > 10:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="La contraseña debe tener entre 4 y 10 caracteres"
        )

    if contrasena.isdigit():

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="La contraseña no puede contener solo numeros"
        )

    if re.search(r"[!#$%&@_-]", contrasena):

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="La contraseña no puede contener simbolos"
        )

    # -----------------------------------
    # VALIDAR EMPLEADO EXISTENTE
    # -----------------------------------

    cursor.execute(
        """
        SELECT id
        FROM empleados
        WHERE cliente_id = %s
        """,
        (cliente["id"],)
    )

    empleado_existente = cursor.fetchone()

    if empleado_existente:

        conexion.close()

        return render_template(
            "empleados-html/crud/crear_employ.html",
            error="Ya eres un empleado"
        )

    # -----------------------------------
    # GENERAR ID
    # -----------------------------------

    while True:

        id_empleado = str(
            random.randint(1000, 9999)
        )

        cursor.execute(
            """
            SELECT id
            FROM empleados
            WHERE id_empleado = %s
            """,
            (id_empleado,)
        )

        existe = cursor.fetchone()

        if not existe:
            break

    # -----------------------------------
    # INSERTAR EMPLEADO
    # -----------------------------------

    cursor.execute(
        """
        INSERT INTO empleados
        (
            cliente_id,
            id_empleado,
            contrasena,
            cargo,
            salario
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            cliente["id"],
            id_empleado,
            contrasena,
            "Empleado Junior",
            0
        )
    )

    # -----------------------------------
    # ACTUALIZAR CLIENTE
    # -----------------------------------

    cursor.execute(
        """
        UPDATE clientes
        SET es_empleado = TRUE
        WHERE id = %s
        """,
        (cliente["id"],)
    )

    conexion.commit()

    conexion.close()

    return render_template(
        "empleados-html/crud/crear_employ.html",
        id_generado=id_empleado,
        mensaje = "Identidad creada exitosamente" 
    )
    
# -----------------------------------
# VALIDAR EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/modificar-pin-validar-employ",
    methods=["GET", "POST"]
)
def modificar_pin_validar_employ():

    # -----------------------------------
    # ABRIR FORMULARIO
    # -----------------------------------

    if request.method == "GET":

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html"
        )

    documento = request.form["documento"].strip()

    email = request.form["email"].strip()

    telefono = request.form["telefono"].strip()

    # -----------------------------------
    # VALIDACIONES
    # -----------------------------------

    if not documento.isdigit():

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="El documento solo debe contener numeros"
        )

    if len(documento) < 6 or len(documento) > 10:

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="El documento debe tener entre 6 y 10 digitos"
        )

    if not telefono.isdigit():

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="El telefono solo debe contener numeros"
        )

    if len(telefono) != 10:

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="El telefono debe tener 10 digitos"
        )

    if "@" not in email:

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="Email invalido"
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # VALIDAR CLIENTE
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE documento = %s
        AND email = %s
        AND telefono = %s
        """,
        (
            documento,
            email,
            telefono
        )
    )

    cliente = cursor.fetchone()

    if not cliente:

        conexion.close()

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="Los datos no coinciden"
        )

    # -----------------------------------
    # VALIDAR EMPLEADO
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM empleados
        WHERE cliente_id = %s
        """,
        (cliente["id"],)
    )

    empleado = cursor.fetchone()

    conexion.close()

    if not empleado:

        return render_template(
            "empleados-html/crud/modificar_pin_validar_employ.html",
            error="No existe identidad de empleado"
        )

    session["empleado_reset_id"] = empleado["id"]

    session["empleado_reset_nombre"] = cliente["nombre"]

    return redirect(
        url_for("empleados.modificar_pin_employ")
    )
    
# -----------------------------------
# MODIFICAR CONTRASEÑA EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/modificar-pin-employ",
    methods=["GET", "POST"]
)
def modificar_pin_employ():

    if "empleado_reset_id" not in session:

        return redirect(
            url_for("empleados.modificar_pin_validar_employ")
        )

    empleado_id = session["empleado_reset_id"]

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT *
        FROM empleados
        WHERE id = %s
        """,
        (empleado_id,)
    )

    empleado = cursor.fetchone()

    if request.method == "POST":

        contrasena = request.form["contrasena"].strip()

        confirmar_contrasena = request.form["confirmar_contrasena"].strip()

        # -----------------------------------
        # VALIDACIONES
        # -----------------------------------

        if not contrasena:

            conexion.close()

            return render_template(
                "empleados-html/crud/modificar_pin_employ.html",
                usuario=session["empleado_reset_nombre"],
                id_empleado=empleado["id_empleado"],
                error="La contraseña no puede estar vacia"
            )

        if len(contrasena) < 4 or len(contrasena) > 10:

            conexion.close()

            return render_template(
                "empleados-html/crud/modificar_pin_employ.html",
                usuario=session["empleado_reset_nombre"],
                id_empleado=empleado["id_empleado"],
                error="La contraseña debe tener entre 4 y 10 caracteres"
            )

        simbolos = "!#$%&@_-"

        if any(simbolo in contrasena for simbolo in simbolos):

            conexion.close()

            return render_template(
                "empleados-html/crud/modificar_pin_employ.html",
                usuario=session["empleado_reset_nombre"],
                id_empleado=empleado["id_empleado"],
                error="La contraseña no puede contener simbolos"
            )

        if contrasena.isdigit():

            conexion.close()

            return render_template(
                "empleados-html/crud/modificar_pin_employ.html",
                usuario=session["empleado_reset_nombre"],
                id_empleado=empleado["id_empleado"],
                error="La contraseña no puede contener solo numeros"
            )

        if contrasena != confirmar_contrasena:

            conexion.close()

            return render_template(
                "empleados-html/crud/modificar_pin_employ.html",
                usuario=session["empleado_reset_nombre"],
                id_empleado=empleado["id_empleado"],
                error="Las contraseñas no coinciden"
            )

        # -----------------------------------
        # ACTUALIZAR CONTRASEÑA
        # -----------------------------------

        cursor.execute(
            """
            UPDATE empleados
            SET contrasena = %s
            WHERE id = %s
            """,
            (
                contrasena,
                empleado_id
            )
        )

        conexion.commit()

        conexion.close()

        session.pop("empleado_reset_id", None)

        session.pop("empleado_reset_nombre", None)

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion.close()

    return render_template(
        "empleados-html/crud/modificar_pin_employ.html",
        usuario=session["empleado_reset_nombre"],
        id_empleado=empleado["id_empleado"]
    )
    
# -----------------------------------
# CATALOGO EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/catalogo-employ"
)
def catalogo_employ():

    # -----------------------------------
    # VALIDAR SESION
    # -----------------------------------

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # OBTENER MEDICAMENTOS
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM medicamentos
        ORDER BY nombre_medicamento ASC
        """
    )

    medicamentos = cursor.fetchall()

    conexion.close()

    return render_template(
        "empleados-html/catalogo_employ.html",
        medicamentos=medicamentos,
        usuario=session.get("empleado_nombre")
    )
# -----------------------------------
# FORMULARIO AGREGAR MEDICAMENTO
# -----------------------------------

@empleados_bp.route(
    "/agregar-medicamento",
    methods=["GET"]
)
def agregar_medicamento_employ():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    return render_template(
        "empleados-html/agregar_medicamento_employ.html"
    )

# -----------------------------------
# AGREGAR MEDICAMENTO
# -----------------------------------

@empleados_bp.route(
    "/agregar-medicamento",
    methods=["POST"]
)
def agregar_medicamento():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    nombre_medicamento = request.form["nombre_medicamento"].strip()

    formula_quimica = request.form["formula_quimica"].strip()

    descripcion_medicamento = request.form["descripcion_medicamento"].strip()

    cantidad_pastas = request.form["cantidad_pastas"].strip()

    precio = request.form["precio"].strip()

    incluido_pbs = request.form["incluido_pbs"]

    stock = request.form["stock"].strip()
    
    imagen_card = "sin-imagen.png"
    
    imagen_empaque = "sin-imagen.png"
    
    imagen_producto = "sin-imagen.png"

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # VALIDACIONES
    # -----------------------------------

    if len(nombre_medicamento) < 3:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El nombre del medicamento es muy corto"
        )

    if len(formula_quimica) < 3:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="Formula quimica invalida"
        )

    if len(descripcion_medicamento) < 10:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="La descripcion es muy corta"
        )

    if not precio.isdigit():

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El precio solo debe contener numeros"
        )

    if int(precio) <= 0:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El precio debe ser mayor a 0"
        )

    if not stock.isdigit():

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El stock solo debe contener numeros"
        )

    if int(stock) <= 0:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El stock debe ser mayor a 0"
        )

    # -----------------------------------
    # VALIDAR MEDICAMENTO
    # -----------------------------------

    cursor.execute(
        """
        SELECT id
        FROM medicamentos
        WHERE nombre_medicamento = %s
        """,
        (nombre_medicamento,)
    )

    medicamento = cursor.fetchone()

    if medicamento:

        conexion.close()

        return render_template(
            "empleados-html/agregar_medicamento_employ.html",
            error="El medicamento ya existe"
        )

    # -----------------------------------
    # INSERTAR MEDICAMENTO
    # -----------------------------------

    nombre_medicamento = nombre_medicamento.lower().capitalize()

    cursor.execute(
        """
        INSERT INTO medicamentos
        (
            nombre_medicamento,
            formula_quimica,
            descripcion_medicamento,
            cantidad_pastas,
            precio,
            incluido_pbs,
            stock,
            imagen_card,
            imagen_empaque,
            imagen_producto
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            nombre_medicamento,
            formula_quimica,
            descripcion_medicamento,
            cantidad_pastas,
            precio,
            incluido_pbs,
            stock,
            imagen_card,
            imagen_empaque,
            imagen_producto
        )
    )

    conexion.commit()

    conexion.close()

    return render_template(
        "empleados-html/agregar_medicamento_employ.html",
        mensaje="Medicamento agregado correctamente"
    )

# -----------------------------------
# REPORTE INVENTARIO
# -----------------------------------

@empleados_bp.route(
    "/reporte-inventario"
)
def reporte_inventario():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            id,
            nombre_medicamento,
            formula_quimica,
            descripcion_medicamento,
            cantidad_pastas,
            precio,
            incluido_pbs,
            stock
        FROM medicamentos
        """
    )

    inventario = cursor.fetchall()

    conexion.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        leading=14,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=10,
        leading=12,
    )

    elementos = []
    elementos.append(Paragraph("REPORTE: INVENTARIO ACTUAL", title_style))
    elementos.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elementos.append(Spacer(1, 12))

    datos_tabla = [
        [
            "ID",
            "Nombre",
            "Formula",
            "Descripcion",
            "Cantidad",
            "Precio",
            "Incluido PBS",
            "Stock",
        ]
    ]

    for medicamento in inventario:
        datos_tabla.append([
            medicamento["id"],
            medicamento["nombre_medicamento"],
            medicamento["formula_quimica"],
            medicamento["descripcion_medicamento"],
            medicamento["cantidad_pastas"],
            f"$ {medicamento['precio']}",
            "Si" if medicamento["incluido_pbs"] in (1, '1', True) else "No",
            medicamento["stock"],
        ])

    tabla = Table(datos_tabla, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ])
    )

    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=inventario-actual.pdf"
    return response


# -----------------------------------
# REPORTE CLIENTES
# -----------------------------------

@empleados_bp.route(
    "/reporte-clientes"
)
def reporte_clientes():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM clientes
        """
    )

    total_clientes = cursor.fetchone()

    conexion.close()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id, nombre, telefono, email, direccion
        FROM usuarios
        """
    )
    usuarios = cursor.fetchall()

    cursor.execute(
        """
        SELECT id, nombre, telefono, email, direccion, es_empleado
        FROM clientes
        """
    )
    clientes = cursor.fetchall()

    conexion.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        leading=14,
    )

    elementos = []
    elementos.append(Paragraph("REPORTE: USUARIOS Y CLIENTES REGISTRADOS", title_style))
    elementos.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elementos.append(Spacer(1, 12))

    elementos.append(Paragraph("Usuarios registrados:", heading_style))
    if usuarios:
        for indice, usuario in enumerate(usuarios, start=1):
            linea = (
                f"{indice}. Nombre: {usuario['nombre']}, "
                f"ID: {usuario['id']}, "
                f"Teléfono: {usuario['telefono']}, "
                f"Gmail: {usuario['email']}, "
                f"Dirección: {usuario['direccion']}"
            )
            elementos.append(Paragraph(linea, normal_style))
            elementos.append(Spacer(1, 6))
    else:
        elementos.append(Paragraph("No hay usuarios registrados.", normal_style))

    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph("Clientes registrados:", heading_style))
    if clientes:
        for indice, cliente in enumerate(clientes, start=1):
            es_empleado = "SI" if cliente["es_empleado"] in (1, '1', True) else "NO"
            linea = (
                f"{indice}. Nombre: {cliente['nombre']}, "
                f"ID: {cliente['id']}, "
                f"Teléfono: {cliente['telefono']}, "
                f"Gmail: {cliente['email']}, "
                f"Dirección: {cliente['direccion']}, "
                f"Es empleado: {es_empleado}"
            )
            elementos.append(Paragraph(linea, normal_style))
            elementos.append(Spacer(1, 6))
    else:
        elementos.append(Paragraph("No hay clientes registrados.", normal_style))

    doc.build(elementos)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=clientes.pdf"
    return response


# -----------------------------------
# REPORTE FACTURAS
# -----------------------------------

@empleados_bp.route(
    "/reporte-facturas"
)
def reporte_facturas():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT SUM(total) AS total_facturas
        FROM facturas
        """
    )

    total_facturas = cursor.fetchone()

    conexion.close()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT *
        FROM facturas
        ORDER BY id ASC
        """
    )
    facturas = cursor.fetchall()

    conexion.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        leading=14,
    )

    elementos = []
    elementos.append(Paragraph("REPORTE: TOTAL FACTURAS", title_style))
    elementos.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elementos.append(Spacer(1, 12))

    datos_tabla = [
        [
            "ID",
            "Persona ID",
            "Tipo persona",
            "Medicamento ID",
            "Solicitud ID",
            "Subtotal",
            "Total",
            "Fecha factura",
            "Método pago",
        ]
    ]

    for factura in facturas:
        fecha_factura = factura["fecha_factura"]
        fecha_str = fecha_factura.strftime("%d/%m/%Y %H:%M") if hasattr(fecha_factura, "strftime") else str(fecha_factura)
        datos_tabla.append([
            factura["id"],
            factura["persona_id"],
            factura["tipo_persona"],
            factura["medicamento_id"],
            factura["solicitud_id"],
            f"$ {factura['subtotal']}",
            f"$ {factura['total']}",
            fecha_str,
            factura["metodo_pago"],
        ])

    tabla = Table(datos_tabla, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ])
    )

    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=total-facturas.pdf"
    return response
    

# -----------------------------------
# GENERAR TAREAS
# -----------------------------------

def generar_tareas(cursor):

    tareas = []

    # OBTENER MEDICAMENTOS

    cursor.execute(
        """
        SELECT
            id,
            nombre_medicamento,
            stock,
            precio
        FROM medicamentos
        ORDER BY RAND()
        LIMIT 3
        """
    )

    medicamentos = cursor.fetchall()

    if len(medicamentos) >= 3:

        medicamento_1 = medicamentos[0]

        medicamento_2 = medicamentos[1]

        medicamento_3 = medicamentos[2]

        tareas.append(
            {
                "descripcion": f"Agrega 40 cantidades al stock de {medicamento_1['nombre_medicamento']}",
                "tipo_tarea": "agregar_stock",
                "medicamento_id": medicamento_1["id"],
                "objetivo": 40
            }
        )

        tareas.append(
            {
                "descripcion": f"Reduce 20 cantidades al stock de {medicamento_2['nombre_medicamento']}",
                "tipo_tarea": "reducir_stock",
                "medicamento_id": medicamento_2["id"],
                "objetivo": 20
            }
        )

        tareas.append(
            {
                "descripcion": f"Modifica el precio del medicamento {medicamento_3['nombre_medicamento']}",
                "tipo_tarea": "modificar_precio",
                "medicamento_id": medicamento_3["id"],
                "objetivo": 1
            }
        )

        tareas.append(
            {
                "descripcion": "Agrega 3 medicamentos nuevos al catalogo",
                "tipo_tarea": "crear_medicamentos",
                "objetivo": 3
            }
        )

    return tareas


# -----------------------------------
# GESTION EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/gestion-empleado",
    methods=["GET", "POST"]
)
def gestion_empleado():

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    empleado_id = session["empleado_id"]

    cliente_id = session.get("cliente_id")

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # OBTENER EMPLEADO
    # -----------------------------------

    cursor.execute(
        """
        SELECT
            empleados.id,
            empleados.id_empleado,
            empleados.salario,
            clientes.nombre,
            clientes.documento,
            clientes.email,
            clientes.telefono,
            clientes.direccion,
            clientes.pin,
            clientes.saldo
        FROM empleados

        INNER JOIN clientes
            ON empleados.cliente_id = clientes.id

        WHERE empleados.id = %s
        """,
        (empleado_id,)
    )

    usuario = cursor.fetchone()

    # -----------------------------------
    # CREAR TAREAS
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM tareas_empleado
        WHERE empleado_id = %s
        """,
        (empleado_id,)
    )

    tareas_existentes = cursor.fetchall()

    if not tareas_existentes:

        tareas = generar_tareas(cursor)

        for tarea in tareas:

            cursor.execute(
                """
                INSERT INTO tareas_empleado
                (
                    empleado_id,
                    descripcion,
                    tipo_tarea,
                    medicamento_id,
                    objetivo,
                    progreso,
                    completada
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    empleado_id,
                    tarea["descripcion"],
                    tarea["tipo_tarea"],
                    tarea.get("medicamento_id"),
                    tarea["objetivo"],
                    0,
                    False
                )
            )

        conexion.commit()

    # -----------------------------------
    # POST
    # -----------------------------------

    if request.method == "POST":

        accion = request.form["accion"]

        # -----------------------------------
        # TRANSFERIR SALARIO
        # -----------------------------------

        if accion == "transferir_salario":

            if usuario["salario"] <= 0:

                conexion.close()

                return render_template(
                    "empleados-html/crud/gestion_employ.html",
                    usuario=usuario,
                    tareas=tareas_existentes,
                    error="No tienes salario disponible"
                )

            salario = float(usuario["salario"])

            # SUMAR AL SALDO

            cursor.execute(
                """
                UPDATE clientes
                SET saldo = saldo + %s
                WHERE id = %s
                """,
                (
                    salario,
                    cliente_id
                )
            )

            # REINICIAR SALARIO

            cursor.execute(
                """
                UPDATE empleados
                SET salario = 0
                WHERE id = %s
                """,
                (empleado_id,)
            )

            conexion.commit()

            mensaje = "Salario transferido correctamente"

        # -----------------------------------
        # COMPLETAR TAREA
        # -----------------------------------

        elif accion == "completar_tarea":

            tarea_id = request.form["tarea_id"]

            cursor.execute(
                """
                UPDATE tareas_empleado
                SET
                    progreso = objetivo,
                    completada = TRUE
                WHERE id = %s
                AND empleado_id = %s
                """,
                (
                    tarea_id,
                    empleado_id
                )
            )

            conexion.commit()

            # VALIDAR TAREAS

            cursor.execute(
                """
                SELECT *
                FROM tareas_empleado
                WHERE empleado_id = %s
                AND completada = FALSE
                """,
                (empleado_id,)
            )

            tareas_pendientes = cursor.fetchall()

            if not tareas_pendientes:

                # RECOMPENSA

                cursor.execute(
                    """
                    UPDATE empleados
                    SET salario = salario + 20000
                    WHERE id = %s
                    """,
                    (empleado_id,)
                )

                # ELIMINAR TAREAS

                cursor.execute(
                    """
                    DELETE FROM tareas_empleado
                    WHERE empleado_id = %s
                    """,
                    (empleado_id,)
                )

                # CREAR NUEVAS

                nuevas_tareas = generar_tareas(cursor)

                for tarea in nuevas_tareas:

                    cursor.execute(
                        """
                        INSERT INTO tareas_empleado
                        (
                            empleado_id,
                            descripcion,
                            tipo_tarea,
                            medicamento_id,
                            objetivo,
                            progreso,
                            completada
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            empleado_id,
                            tarea["descripcion"],
                            tarea["tipo_tarea"],
                            tarea.get("medicamento_id"),
                            tarea["objetivo"],
                            0,
                            False
                        )
                    )

                mensaje = "Completaste todas las tareas. Ganaste $20.000"

            else:

                mensaje = "Tarea completada"

            conexion.commit()

        # -----------------------------------
        # ELIMINAR EMPLEADO
        # -----------------------------------

        elif accion == "eliminar":

            pin = request.form["pin"]

            if pin != usuario["pin"]:

                cursor.execute(
                    """
                    SELECT *
                    FROM tareas_empleado
                    WHERE empleado_id = %s
                    """,
                    (empleado_id,)
                )

                tareas = cursor.fetchall()

                conexion.close()

                return render_template(
                    "empleados-html/crud/gestion_employ.html",
                    usuario=usuario,
                    tareas=tareas,
                    error_delete="PIN incorrecto"
                )

            # ELIMINAR EMPLEADO

            cursor.execute(
                """
                DELETE FROM empleados
                WHERE id = %s
                """,
                (empleado_id,)
            )

            # ACTUALIZAR CLIENTE

            cursor.execute(
                """
                UPDATE clientes
                SET es_empleado = FALSE
                WHERE id = %s
                """,
                (cliente_id,)
            )

            conexion.commit()

            conexion.close()

            session.clear()

            return redirect(
                url_for("empleados.login_employ")
            )

    # -----------------------------------
    # OBTENER TAREAS
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM tareas_empleado
        WHERE empleado_id = %s
        """,
        (empleado_id,)
    )

    tareas = cursor.fetchall()

    # RECARGAR DATOS

    cursor.execute(
        """
        SELECT
            empleados.id,
            empleados.id_empleado,
            empleados.salario,
            clientes.nombre,
            clientes.documento,
            clientes.email,
            clientes.telefono,
            clientes.direccion,
            clientes.pin,
            clientes.saldo
        FROM empleados

        INNER JOIN clientes
            ON empleados.cliente_id = clientes.id

        WHERE empleados.id = %s
        """,
        (empleado_id,)
    )

    usuario = cursor.fetchone()

    conexion.close()

    return render_template(
        "empleados-html/crud/gestion_employ.html",
        usuario=usuario,
        tareas=tareas,
        mensaje=locals().get("mensaje"),
        error=locals().get("error"),
        error_delete=locals().get("error_delete")
    )
    
# -----------------------------------
# VER MEDICAMENTO EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/ver-medicamento-employ/<int:id>",
    methods=["GET", "POST"]
)
def ver_medicamento_employ(id):

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )
    
    if "cliente_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT *
        FROM medicamentos
        WHERE id = %s
        """,
        (id,)
    )

    medicamento = cursor.fetchone()

    if not medicamento:

        conexion.close()

        return redirect(
            url_for("empleados.catalogo_employ")
        )

    # -----------------------------------
    # ACTUALIZAR DATOS
    # -----------------------------------

    if request.method == "POST":

        accion = request.form.get("accion")

        if accion == "eliminar_medicamento":

            if medicamento["imagen_card"] != "sin-imagen.png":

                conexion.close()

                return render_template(
                    "empleados-html/ver_medicamento_employ.html",
                    medicamento=medicamento,
                    error="Solo los medicamentos creados manualmente se pueden eliminar"
                )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM facturas
                WHERE medicamento_id = %s
                """,
                (id,)
            )

            factura_relacionada = cursor.fetchone()

            if factura_relacionada and factura_relacionada["total"] > 0:

                conexion.close()

                return render_template(
                    "empleados-html/ver_medicamento_employ.html",
                    medicamento=medicamento,
                    error="No se puede eliminar este medicamento porque tiene facturas relacionadas"
                )

            cursor.execute(
                """
                DELETE FROM medicamentos
                WHERE id = %s
                """,
                (id,)
            )

            conexion.commit()

            conexion.close()

            return redirect(
                url_for("empleados.catalogo_employ")
            )

        nombre_medicamento = request.form["nombre_medicamento"].strip()

        descripcion_medicamento = request.form["descripcion_medicamento"].strip()

        formula_quimica = request.form["formula_quimica"].strip()

        cantidad_pastas = request.form["cantidad_pastas"].strip()

        precio = request.form["precio"].strip()

        stock = request.form["stock"].strip()

        incluido_pbs = request.form.get("incluido_pbs", "No")

        # VALIDACIONES

        if not nombre_medicamento:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="El nombre no puede estar vacio"
            )

        if len(nombre_medicamento) < 3:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="Nombre demasiado corto"
            )

        if not descripcion_medicamento:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="La descripcion no puede estar vacia"
            )

        if len(descripcion_medicamento) < 10:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="Descripcion demasiado corta"
            )

        if not formula_quimica:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="La formula no puede estar vacia"
            )

        if not cantidad_pastas:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="La cantidad no puede estar vacia"
            )

        if not precio.isdigit():

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="El precio solo debe contener numeros"
            )

        if int(precio) <= 0:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="Precio invalido"
            )

        if not stock.isdigit():

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="El stock solo debe contener numeros"
            )

        if int(stock) < 0:

            conexion.close()

            return render_template(
                "empleados-html/ver_medicamento_employ.html",
                medicamento=medicamento,
                error="Stock invalido"
            )

        # UPDATE

        cursor.execute(
            """
            UPDATE medicamentos
            SET
                nombre_medicamento = %s,
                descripcion_medicamento = %s,
                formula_quimica = %s,
                cantidad_pastas = %s,
                precio = %s,
                stock = %s,
                incluido_pbs = %s
            WHERE id = %s
            """,
            (
                nombre_medicamento,
                descripcion_medicamento,
                formula_quimica,
                cantidad_pastas,
                precio,
                stock,
                incluido_pbs,
                id
            )
        )

        conexion.commit()

        # RECARGAR DATOS

        cursor.execute(
            """
            SELECT *
            FROM medicamentos
            WHERE id = %s
            """,
            (id,)
        )

        medicamento = cursor.fetchone()

        conexion.close()

        return render_template(
            "empleados-html/ver_medicamento_employ.html",
            medicamento=medicamento,
            mensaje="Medicamento actualizado correctamente"
        )

    conexion.close()

    return render_template(
        "empleados-html/ver_medicamento_employ.html",
        medicamento=medicamento
    )
    
# -----------------------------------
# ENVIO MEDICAMENTO EMPLEADO
# -----------------------------------

@empleados_bp.route(
    "/envio-medicamento-employ",
    methods=["GET", "POST"]
)
def envio_medicamento_employ():

    # VALIDAR SESION

    if "empleado_id" not in session:

        return redirect(
            url_for("empleados.login_employ")
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    mensaje = None
    error = None

    if request.method == "POST":

        fecha_id = request.form.get("fecha_id")
        fecha_nueva = request.form.get("fecha_nueva")

        if not fecha_id or not fecha_nueva:
            error = "Debes seleccionar una fecha activa y una nueva fecha."
        else:
            cursor.execute(
                """
                SELECT id, fecha
                FROM fechas_disponibles
                ORDER BY id ASC
                LIMIT 4
                """
            )

            fechas_activas = cursor.fetchall()
            ids_activas = [str(fecha["id"]) for fecha in fechas_activas]

            if fecha_id not in ids_activas:
                error = "Fecha activa no válida."
            else:
                cursor.execute(
                    """
                    SELECT *
                    FROM fechas_disponibles
                    WHERE id = %s
                    """,
                    (fecha_id,)
                )

                fecha_activa = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT *
                    FROM fechas_disponibles
                    WHERE fecha = %s
                    """,
                    (fecha_nueva,)
                )

                fecha_existente = cursor.fetchone()

                if not fecha_activa or not fecha_existente:
                    error = "Fecha seleccionada no existe."
                elif fecha_activa["fecha"] == fecha_nueva:
                    mensaje = "No se realizó ningún cambio. La fecha ya estaba activa."
                else:
                    placeholder = "9999-12-31"
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS total
                        FROM fechas_disponibles
                        WHERE fecha = %s
                        """,
                        (placeholder,)
                    )
                    existente_placeholder = cursor.fetchone()

                    if existente_placeholder["total"] > 0:
                        placeholder = "9999-12-30"

                    cursor.execute(
                        """
                        UPDATE fechas_disponibles
                        SET fecha = %s
                        WHERE id = %s
                        """,
                        (placeholder, fecha_id)
                    )

                    cursor.execute(
                        """
                        UPDATE fechas_disponibles
                        SET fecha = %s
                        WHERE id = %s
                        """,
                        (fecha_activa["fecha"], fecha_existente["id"])
                    )

                    cursor.execute(
                        """
                        UPDATE fechas_disponibles
                        SET fecha = %s
                        WHERE id = %s
                        """,
                        (fecha_nueva, fecha_id)
                    )

                    conexion.commit()
                    mensaje = "Fechas actualizadas correctamente"

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY id ASC
        LIMIT 4
        """
    )

    fechas_activas = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY fecha ASC
        """
    )

    todas_fechas = cursor.fetchall()

    conexion.close()

    return render_template(
        "empleados-html/envio_medicamento_employ.html",
        fechas_activas=fechas_activas,
        todas_fechas=todas_fechas,
        mensaje=mensaje,
        error=error
    )