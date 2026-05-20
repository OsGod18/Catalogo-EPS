from flask import Blueprint, render_template, request, redirect, send_file, session, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from database import obtener_conexion

import io

clientes_bp = Blueprint(
    "clientes",
    __name__
)

# -----------------------------------
# LOGIN CLIENT
# -----------------------------------

@clientes_bp.route("/login-client")
def login_client():

    return render_template(
        "clientes-html/login_client.html"
    )
    
# -----------------------------------
# VALIDAR LOGIN CLIENT
# -----------------------------------

@clientes_bp.route(
    "/validar-login-client",
    methods=["POST"]
)
def validar_login_client():

    documento = request.form["documento"]

    pin = request.form["pin"]

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT * FROM clientes
        WHERE documento = %s
        AND pin = %s
        """,
        (documento, pin)
    )

    cliente = cursor.fetchone()

    conexion.close()

    if cliente:

        session["cliente_id"] = cliente["id"]

        session["cliente_nombre"] = cliente["nombre"]

        return redirect(
            url_for("clientes.catalogo_client")
        )

    else:

        return render_template(
            "clientes-html/login_client.html",
            error="Documento o PIN incorrecto"
        )

# -----------------------------------
# CATALOGO CLIENT
# -----------------------------------

@clientes_bp.route("/catalogo-client")
def catalogo_client():

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # MEDICAMENTOS

    cursor.execute(
        """
        SELECT * FROM medicamentos
        """
    )

    medicamentos = cursor.fetchall()

    # CLIENTE

    cursor.execute(
        """
        SELECT saldo, es_empleado
        FROM clientes
        WHERE id = %s
        """,
        (session["cliente_id"],)
    )

    cliente = cursor.fetchone()

    conexion.close()

    return render_template(
        "clientes-html/catalogo_client.html",
        usuario=session["cliente_nombre"],
        medicamentos=medicamentos,
        saldo=cliente["saldo"],
        oferta_empleo=(cliente["saldo"] <= 10000 and not cliente["es_empleado"])
    )
    

# -----------------------------------
# VER MEDICAMENTO CLIENT
# -----------------------------------

@clientes_bp.route(
    "/ver-medicamento-client/<int:id>"
)
def ver_medicamento_client(id):

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # MEDICAMENTO

    cursor.execute(
        """
        SELECT * FROM medicamentos
        WHERE id = %s
        """,
        (id,)
    )

    medicamento = cursor.fetchone()

    # CLIENTE

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE id = %s
        """,
        (session["cliente_id"],)
    )

    usuario = cursor.fetchone()

    conexion.close()

    # VALIDAR MEDICAMENTO

    if not medicamento:

        return "Medicamento no encontrado"

    return render_template(
        "clientes-html/ver_medicamento_client.html",
        medicamento=medicamento,
        usuario=usuario
    )
    
# -----------------------------------
# ENVIO CLIENT
# -----------------------------------

@clientes_bp.route("/envio-client")
def envio_client():

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    medicamento = request.args.get(
        "medicamento"
    )

    tipo_entrega = request.args.get(
        "tipo_entrega"
    )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # FECHAS ACTIVAS

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY id ASC
        LIMIT 4
        """
    )

    fechas = cursor.fetchall()

    # OBTENER USUARIO

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE id = %s
        """,
        (session["cliente_id"],)
    )

    usuario = cursor.fetchone()

    conexion.close()

    return render_template(
        "clientes-html/envio_medicamento_client.html",
        medicamento=medicamento,
        tipo_entrega=tipo_entrega,
        fechas=fechas,
        usuario=usuario
    )

# -----------------------------------
# GUARDAR SOLICITUD CLIENT
# -----------------------------------

@clientes_bp.route(
    "/guardar-solicitud-client",
    methods=["POST"]
)
def guardar_solicitud_client():

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    cliente_id = session["cliente_id"]

    medicamento_nombre = request.form["medicamento"]

    tipo_entrega = request.form["tipo_entrega"]

    fecha_entrega = request.form["fecha_entrega"]

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    if not fecha_entrega:
        cursor.execute(
            """
            SELECT *
            FROM fechas_disponibles
            ORDER BY fecha ASC
            """
        )

        fechas = cursor.fetchall()

        conexion.close()

        return render_template(
            "clientes-html/envio_medicamento_client.html",
            mensaje="Selecciona una fecha para la entrega",
            medicamento=medicamento_nombre,
            tipo_entrega=tipo_entrega,
            usuario=cliente,
            fechas=fechas
        )

    # CLIENTE

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE id = %s
        """,
        (cliente_id,)
    )

    cliente = cursor.fetchone()

    # MEDICAMENTO

    cursor.execute(
        """
        SELECT *
        FROM medicamentos
        WHERE nombre_medicamento = %s
        """,
        (medicamento_nombre,)
    )

    medicamento = cursor.fetchone()

    if not medicamento:

        conexion.close()

        return "Medicamento no encontrado"

    # VALIDAR STOCK

    # VALIDAR STOCK

    if medicamento["stock"] <= 0:

        cursor.execute(
            """
            SELECT *
            FROM fechas_disponibles
            ORDER BY fecha ASC
            """
        )

        fechas = cursor.fetchall()

        conexion.close()

        return render_template(
            "clientes-html/envio_medicamento_client.html",
            mensaje="No hay stock disponible",
            medicamento=medicamento_nombre,
            tipo_entrega=tipo_entrega,
            usuario=cliente,
            fechas=fechas
        )

    # VALIDAR SALDO

# VALIDAR SALDO

    if cliente["saldo"] < medicamento["precio"]:

        cursor.execute(
            """
            SELECT *
            FROM fechas_disponibles
            ORDER BY fecha ASC
            """
        )

        fechas = cursor.fetchall()

        conexion.close()

        return render_template(
            "clientes-html/envio_medicamento_client.html",
            mensaje="No tienes saldo",
            medicamento=medicamento_nombre,
            tipo_entrega=tipo_entrega,
            usuario=cliente,
            fechas=fechas
        )

    # DESCONTAR SALDO

    nuevo_saldo = (
        cliente["saldo"] -
        medicamento["precio"]
    )

    cursor.execute(
        """
        UPDATE clientes
        SET saldo = %s
        WHERE id = %s
        """,
        (
            nuevo_saldo,
            cliente_id
        )
    )

    # DESCONTAR STOCK

    nuevo_stock = medicamento["stock"] - 1

    cursor.execute(
        """
        UPDATE medicamentos
        SET stock = %s
        WHERE id = %s
        """,
        (
            nuevo_stock,
            medicamento["id"]
        )
    )

    # CREAR SOLICITUD

    cursor.execute(
        """
        INSERT INTO solicitudes
        (
            persona_id,
            tipo_persona,
            medicamento_id,
            tipo_entrega,
            fecha_entrega
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            cliente_id,
            "cliente",
            medicamento["id"],
            tipo_entrega,
            fecha_entrega
        )
    )

    solicitud_id = cursor.lastrowid

    # FACTURA

    cursor.execute(
        """
        INSERT INTO facturas
        (
            persona_id,
            tipo_persona,
            medicamento_id,
            solicitud_id,
            subtotal,
            total,
            metodo_pago
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            cliente_id,
            "cliente",
            medicamento["id"],
            solicitud_id,
            medicamento["precio"],
            medicamento["precio"],
            "saldo_cliente"
        )
    )

    conexion.commit()

    conexion.close()

    cliente["saldo"] = nuevo_saldo

    # RECARGAR FECHAS

    cursor = obtener_conexion().cursor()

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY fecha ASC
        LIMIT 4
        """
    )

    fechas = cursor.fetchall()

    return render_template(
        "clientes-html/envio_medicamento_client.html",
        mensaje="Compra realizada exitosamente",
        medicamento=medicamento_nombre,
        tipo_entrega=tipo_entrega,
        usuario=cliente,
        fechas=fechas,
        mostrar_factura=True,
        solicitud_id=solicitud_id
    )
    
# -----------------------------------
# GENERAR FACTURA CLIENT
# -----------------------------------

@clientes_bp.route(
    "/generar-factura-client/<int:solicitud_id>"
)
def generar_factura_client(solicitud_id):

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT

            solicitudes.id,
            solicitudes.tipo_entrega,
            solicitudes.fecha_solicitud,
            solicitudes.fecha_entrega,

            medicamentos.nombre_medicamento,
            medicamentos.descripcion_medicamento,
            medicamentos.formula_quimica,
            medicamentos.precio,

            clientes.nombre,
            clientes.documento,
            clientes.email,
            clientes.telefono,
            clientes.saldo

        FROM solicitudes

        INNER JOIN medicamentos
            ON solicitudes.medicamento_id = medicamentos.id

        INNER JOIN clientes
            ON solicitudes.persona_id = clientes.id

        WHERE solicitudes.id = %s
        """,
        (solicitud_id,)
    )

    datos = cursor.fetchone()

    conexion.close()

    if not datos:

        return "Factura no encontrada"

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        180,
        750,
        "FACTURA CLIENTE"
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        50,
        700,
        "DATOS DEL CLIENTE"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        675,
        f"Nombre: {datos['nombre']}"
    )

    pdf.drawString(
        50,
        655,
        f"Documento: {datos['documento']}"
    )

    pdf.drawString(
        50,
        635,
        f"Telefono: {datos['telefono']}"
    )

    pdf.drawString(
        50,
        615,
        f"Correo: {datos['email']}"
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        50,
        570,
        "MEDICAMENTO"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        545,
        f"Medicamento: {datos['nombre_medicamento']}"
    )

    pdf.drawString(
        50,
        525,
        f"Formula: {datos['formula_quimica']}"
    )

    pdf.drawString(
        50,
        505,
        f"Entrega: {datos['tipo_entrega']}"
    )

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        50,
        460,
        "FECHAS"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        435,
        f"Solicitud: {datos['fecha_solicitud']}"
    )

    pdf.drawString(
        50,
        415,
        f"Entrega: {datos['fecha_entrega']}"
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        360,
        f"TOTAL PAGADO: ${datos['precio']}"
    )

    pdf.drawString(
        50,
        330,
        f"SALDO DISPONIBLE: ${datos['saldo']}"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        280,
        "Gracias por utilizar CatalogoEPS."
    )

    pdf.drawString(
        50,
        260,
        "Tu medicamento sera entregado en la fecha seleccionada."
    )

    pdf.showPage()

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="factura_cliente.pdf",
        mimetype="application/pdf"
    )


# -----------------------------------
# LOGOUT CLIENT
# -----------------------------------

@clientes_bp.route("/logout-client")
def logout_client():

    session.clear()

    return redirect(
        url_for("clientes.login_client")
    )
    
# -----------------------------------
# GESTION CLIENT
# -----------------------------------

@clientes_bp.route(
    "/gestion-client",
    methods=["GET", "POST"]
)
def gestion_client():

    if "cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    cliente_id = session["cliente_id"]

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -----------------------------------
    # OBTENER CLIENTE
    # -----------------------------------

    cursor.execute(
        """
        SELECT *
        FROM clientes
        WHERE id = %s
        """,
        (cliente_id,)
    )

    usuario = cursor.fetchone()

    # -----------------------------------
    # OBTENER SOLICITUDES
    # -----------------------------------

    cursor.execute(
        """
        SELECT

            solicitudes.tipo_entrega,
            solicitudes.fecha_solicitud,
            solicitudes.fecha_entrega,

            medicamentos.nombre_medicamento AS nombre,
            medicamentos.precio

        FROM solicitudes

        INNER JOIN medicamentos
            ON solicitudes.medicamento_id = medicamentos.id

        WHERE solicitudes.persona_id = %s
        AND solicitudes.tipo_persona = 'cliente'

        ORDER BY solicitudes.fecha_solicitud DESC
        """,
        (cliente_id,)
    )

    solicitudes = cursor.fetchall()

    # -----------------------------------
    # POST
    # -----------------------------------

    if request.method == "POST":

        accion = request.form["accion"]

        # -----------------------------------
        # ACTUALIZAR
        # -----------------------------------

        if accion == "actualizar":

            nombre = request.form["nombre"].strip()

            documento = request.form["documento"].strip()

            email = request.form["email"].strip()

            telefono = request.form["telefono"].strip()

            direccion = request.form["direccion"].strip()


            # -----------------------------------
            # VALIDACIONES
            # -----------------------------------

            # DOCUMENTO

            if not documento.isdigit():

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El documento solo debe contener números"
                )

            if len(documento) < 6 or len(documento) > 10:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El documento debe tener entre 6 y 10 dígitos"
                )

            if len(set(documento)) == 1:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El documento no puede tener todos los dígitos iguales"
                )

            # NOMBRE

            if not nombre.replace(" ", "").isalpha():

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El nombre solo debe contener letras"
                )

            if len(nombre) < 3 or len(nombre) > 50:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El nombre debe tener entre 3 y 50 caracteres"
                )

            if len(set(nombre.replace(" ", ""))) == 1:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El nombre no puede contener una misma cadena repetida"
                )

            # TELEFONO

            if not telefono.isdigit():

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El teléfono solo debe contener dígitos"
                )

            if len(telefono) != 10:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El teléfono debe tener 10 dígitos"
                )

            if len(set(telefono)) == 1:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El teléfono no puede tener todos los dígitos iguales"
                )

            # EMAIL

            dominios_validos = [
                "gmail.com",
                "outlook.com",
                "hotmail.com",
                "yahoo.com"
            ]

            if "@" not in email:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El email debe contener @"
                )

            dominio = email.split("@")[-1]

            if dominio not in dominios_validos:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="Dominio de email no válido"
                )

            if len(email) < 10:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="El email debe tener al menos 10 caracteres"
                )

            # DIRECCION

            if len(set(direccion.replace(" ", ""))) == 1:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="La dirección no puede tener todos los caracteres iguales"
                )

            if len(direccion) < 10:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error="La dirección debe tener al menos 10 caracteres"
                )
                
            # -----------------------------------
            # ACTUALIZAR DATOS
            # -----------------------------------

            cursor.execute(
                """
                UPDATE clientes
                SET

                    nombre = %s,
                    documento = %s,
                    email = %s,
                    telefono = %s,
                    direccion = %s

                WHERE id = %s
                """,
                (
                    nombre,
                    documento,
                    email,
                    telefono,
                    direccion,
                    cliente_id
                )
            )

            conexion.commit()

            session["cliente_nombre"] = nombre

            # -----------------------------------
            # RECARGAR CLIENTE
            # -----------------------------------

            cursor.execute(
                """
                SELECT *
                FROM clientes
                WHERE id = %s
                """,
                (cliente_id,)
            )

            usuario = cursor.fetchone()

            conexion.close()

            return render_template(
                "clientes-html/crud/gestion_client.html",
                usuario=usuario,
                solicitudes=solicitudes,
                mensaje="Datos actualizados correctamente"
            )

        # -----------------------------------
        # ELIMINAR
        # -----------------------------------

        elif accion == "eliminar":

            pin = request.form["pin"]

            if pin != usuario["pin"]:

                conexion.close()

                return render_template(
                    "clientes-html/crud/gestion_client.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error_delete="PIN incorrecto"
                )

            cursor.execute(
                """
                SELECT id
                FROM empleados
                WHERE cliente_id = %s
                """,
                (cliente_id,)
            )

            empleado = cursor.fetchone()

            if empleado:
                cursor.execute(
                    """
                    DELETE FROM tareas_empleado
                    WHERE empleado_id = %s
                    """,
                    (empleado["id"],)
                )

            cursor.execute(
                """
                DELETE FROM clientes
                WHERE id = %s
                """,
                (cliente_id,)
            )

            conexion.commit()

            conexion.close()

            session.clear()

            return redirect(
                url_for("clientes.login_client")
            )

    conexion.close()

    return render_template(
        "clientes-html/crud/gestion_client.html",
        usuario=usuario,
        solicitudes=solicitudes
    )
# -----------------------------------
# MODIFICAR PIN VALIDAR CLIENT
# -----------------------------------

@clientes_bp.route(
    "/modificar-pin-validar-client",
    methods=["GET", "POST"]
)
def modificar_pin_validar_client():

    # -------------------------
    # ABRIR FORMULARIO
    # -------------------------

    if request.method == "GET":

        return render_template(
            "clientes-html/crud/modificar_pin_validar_client.html"
        )

    # -------------------------
    # RECIBIR DATOS
    # -------------------------
    nombre = request.form["nombre"].strip()

    documento = request.form["documento"].strip()

    email = request.form["email"].strip()

    telefono = request.form["telefono"].strip()

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -------------------------
    # VALIDAR CLIENTE
    # -------------------------

    cursor.execute(
        """
        SELECT * FROM clientes
        WHERE nombre = %s
        AND documento = %s
        AND email = %s
        AND telefono = %s
        """,
        (
            nombre,
            documento,
            email,
            telefono
        )
    )

    cliente = cursor.fetchone()

    conexion.close()

    # -------------------------
    # CLIENTE CORRECTO
    # -------------------------

    if cliente:

        session["recuperar_cliente_id"] = cliente["id"]

        session["recuperar_cliente_nombre"] = cliente["nombre"]

        return redirect(
            url_for("clientes.modificar_pin_client")
        )

    # -------------------------
    # CLIENTE INCORRECTO
    # -------------------------

    else:

        return render_template(
            "clientes-html/crud/modificar_pin_validar_client.html",
            error="Datos incorrectos"
        )
        
# -----------------------------------
# MODIFICAR PIN CLIENT
# -----------------------------------

@clientes_bp.route(
    "/modificar-pin-client",
    methods=["GET", "POST"]
)
def modificar_pin_client():

    # VALIDAR SESION TEMPORAL

    if "recuperar_cliente_id" not in session:

        return redirect(
            url_for("clientes.login_client")
        )

    # SI ES GET

    if request.method == "GET":

        return render_template(
            "clientes-html/crud/modificar_pin_client.html",
            usuario=session["recuperar_cliente_nombre"]
        )

    # SI ES POST

    pin = request.form["pin"]

    confirmar_pin = request.form["confirmar_pin"]

    # VALIDACIONES

    if pin != confirmar_pin:

        return render_template(
            "clientes-html/crud/modificar_pin_client.html",
            usuario=session["recuperar_cliente_nombre"],
            error="Los PIN no coinciden"
        )

    if not pin.isdigit():

        return render_template(
            "clientes-html/crud/modificar_pin_client.html",
            usuario=session["recuperar_cliente_nombre"],
            error="El PIN debe contener solo numeros"
        )

    if len(pin) != 4:

        return render_template(
            "clientes-html/crud/modificar_pin_client.html",
            usuario=session["recuperar_cliente_nombre"],
            error="El PIN debe tener 4 digitos"
        )

    # ACTUALIZAR PIN

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE clientes
        SET pin = %s
        WHERE id = %s
        """,
        (
            pin,
            session["recuperar_cliente_id"]
        )
    )

    conexion.commit()

    conexion.close()

    # ELIMINAR SESION TEMPORAL

    session.pop(
        "cliente_recuperacion_id",
        None
    )

    session.pop(
        "recuperar_cliente_nombre",
        None
    )

    return redirect(
        url_for("clientes.login_client")
    )


# -----------------------------------
# CREAR CLIENT
# -----------------------------------

@clientes_bp.route(
    "/crear-client",
    methods=["GET", "POST"]
)
def crear_client():

    # -------------------------
    # ABRIR FORMULARIO
    # -------------------------

    if request.method == "GET":

        return render_template(
            "clientes-html/crud/crear_client.html"
        )

    # -------------------------
    # RECIBIR DATOS
    # -------------------------

    documento = request.form["documento"].strip()

    nombre = request.form["nombre"].strip()

    telefono = request.form["telefono"].strip()

    email = request.form["email"].strip()

    direccion = request.form["direccion"].strip()

    saldo = request.form["saldo"].strip()

    pin = request.form["pin"].strip()

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -------------------------
    # VALIDACIONES
    # -------------------------

    # DOCUMENTO

    if not documento.isdigit():

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El documento solo debe contener números"
        )

    if len(documento) < 6 or len(documento) > 10:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El documento debe tener entre 6 y 10 dígitos"
        )

    if len(set(documento)) == 1:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El documento no puede tener todos los dígitos iguales"
        )

    # NOMBRE

    if not nombre.replace(" ", "").isalpha():

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El nombre solo debe contener letras"
        )

    if len(nombre) < 3 or len(nombre) > 50:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El nombre debe tener entre 3 y 50 caracteres"
        )

    if len(set(nombre.replace(" ", ""))) == 1:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El nombre no puede contener una misma cadena repetida"
        )

    # PIN

    if not pin.isdigit():

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El PIN solo debe contener números"
        )

    if len(pin) != 4:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El PIN debe tener exactamente 4 dígitos"
        )

    # TELEFONO

    if not telefono.isdigit():

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El teléfono solo debe contener dígitos"
        )

    if len(telefono) != 10:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El teléfono debe tener 10 dígitos"
        )

    if len(set(telefono)) == 1:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El teléfono no puede tener todos los los dígitos iguales"
        )

    # EMAIL

    dominios_validos = [
        "gmail.com",
        "outlook.com",
        "hotmail.com",
        "yahoo.com"
    ]

    if "@" not in email:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El email debe contener @"
        )

    dominio = email.split("@")[-1]

    if dominio not in dominios_validos:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="Dominio de email no válido"
        )

    if len(email) < 10:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El email debe tener al menos 10 caracteres"
        )

    # DIRECCION

    if len(set(direccion.replace(" ", ""))) == 1:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="La dirección no puede tener todos los caracteres iguales"
        )

    if len(direccion) < 10:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="La dirección debe tener al menos 10 caracteres"
        )

        # VALIDAR SALDO

    try:

        saldo = float(saldo)

    except:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El saldo debe ser numerico"
        )

    if saldo < 0:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El saldo no puede ser negativo"
        )

    if saldo > 100000:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El saldo inicial no puede superar 100.000"
        )

    # -------------------------
    # VALIDAR DOCUMENTO
    # -------------------------

    cursor.execute(
        """
        SELECT id
        FROM clientes
        WHERE documento = %s
        """,
        (documento,)
    )

    cliente_existente = cursor.fetchone()

    if cliente_existente:

        conexion.close()

        return render_template(
            "clientes-html/crud/crear_client.html",
            error="El documento ya esta registrado"
        )

    # -------------------------
    # INSERTAR CLIENTE
    # -------------------------

    cursor.execute(
        """
        INSERT INTO clientes
        (
            documento,
            nombre,
            telefono,
            email,
            direccion,
            saldo,
            pin
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            documento,
            nombre,
            telefono,
            email,
            direccion,
            saldo,
            pin
        )
    )

    conexion.commit()

    conexion.close()

    # -------------------------
    # REDIRECCION LOGIN
    # -------------------------

    return redirect(
        url_for("clientes.login_client")
    )

