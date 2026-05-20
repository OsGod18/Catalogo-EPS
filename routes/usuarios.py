# routes/usuarios.py

from flask import Blueprint, render_template, request, redirect, session, url_for
from database import obtener_conexion
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import io


usuarios_bp = Blueprint("usuarios", __name__)



# -----------------------------------
# LOGIN USER
# -----------------------------------

@usuarios_bp.route("/login-user")
def login_user():

    return render_template(
        "usuarios-html/login_user.html"
    )


# -----------------------------------
# VALIDAR LOGIN USER
# -----------------------------------

@usuarios_bp.route("/login-user", methods=["POST"])
def validar_login_user():

    documento = request.form["documento"]
    pin = request.form["pin"]

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM usuarios
        WHERE documento = %s AND pin = %s
    """, (documento, pin))

    usuario = cursor.fetchone()

    conexion.close()

    if usuario:

        session["usuario_id"] = usuario["id"]
        session["usuario_nombre"] = usuario["nombre"]

        return redirect(
            url_for("usuarios.catalogo_user")
        )

    else:

        return render_template(
            "usuarios-html/login_user.html",
            error="Documento o PIN incorrecto"
        )


# -----------------------------------
# CREAR USER
# -----------------------------------

@usuarios_bp.route(
    "/crear-user",
    methods=["GET", "POST"]
)
def crear_user():

    # -------------------------
    # ABRIR FORMULARIO
    # -------------------------

    if request.method == "GET":

        return render_template(
            "usuarios-html/crud/crear_user.html"
        )

    # -------------------------
    # RECIBIR DATOS
    # -------------------------

    documento = request.form["documento"].strip()

    nombre = request.form["nombre"].strip()

    telefono = request.form["telefono"].strip()

    email = request.form["email"].strip().lower()

    direccion = request.form["direccion"].strip()

    pin = request.form["pin"].strip()

    # -------------------------
    # VALIDACIONES
    # -------------------------

    # DOCUMENTO

    if not documento.isdigit():

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El documento solo debe contener números"
        )

    if len(documento) < 6 or len(documento) > 10:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El documento debe tener entre 6 y 10 dígitos"
        )

    if len(set(documento)) == 1:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El documento no puede tener todos los dígitos iguales"
        )

    # NOMBRE

    if not nombre.replace(" ", "").isalpha():

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El nombre solo debe contener letras"
        )

    if len(nombre) < 3 or len(nombre) > 50:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El nombre debe tener entre 3 y 50 caracteres"
        )

    if len(set(nombre.replace(" ", ""))) == 1:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El nombre no puede contener una misma cadena repetida"
        )

    # PIN

    if not pin.isdigit():

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El PIN solo debe contener números"
        )

    if len(pin) != 4:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El PIN debe tener exactamente 4 dígitos"
        )

    # TELEFONO

    if not telefono.isdigit():

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El teléfono solo debe contener dígitos"
        )

    if len(telefono) != 10:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El teléfono debe tener 10 dígitos"
        )

    if len(set(telefono)) == 1:

        return render_template(
            "usuarios-html/crud/crear_user.html",
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

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El email debe contener @"
        )

    dominio = email.split("@")[-1]

    if dominio not in dominios_validos:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="Dominio de email no válido"
        )

    if len(email) < 10:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El email debe tener al menos 10 caracteres"
        )

    # DIRECCION

    if len(set(direccion.replace(" ", ""))) == 1:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="La dirección no puede tener todos los caracteres iguales"
        )

    if len(direccion) < 10:

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="La dirección debe tener al menos 10 caracteres"
        )

    # -------------------------
    # CONEXION
    # -------------------------

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    # -------------------------
    # VALIDAR DOCUMENTO
    # -------------------------

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE documento = %s
        """,
        (documento,)
    )

    usuario_existente = cursor.fetchone()

    if usuario_existente:

        conexion.close()

        return render_template(
            "usuarios-html/crud/crear_user.html",
            error="El documento ya está registrado"
        )

    # -------------------------
    # INSERTAR USER
    # -------------------------

    cursor.execute(
        """
        INSERT INTO usuarios
        (
            documento,
            nombre,
            telefono,
            email,
            direccion,
            pin
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            documento,
            nombre,
            telefono,
            email,
            direccion,
            pin
        )
    )

    conexion.commit()

    conexion.close()

    # -------------------------
    # REDIRECCION LOGIN
    # -------------------------

    return redirect(
        url_for("usuarios.login_user")
    )

# -----------------------------------
# CATALOGO USER
# -----------------------------------

@usuarios_bp.route("/catalogo-user")
def catalogo_user():

    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM medicamentos"
    )



    medicamentos = cursor.fetchall()


    conexion.close()

    return render_template(
        "usuarios-html/catalogo_user.html",
        usuario=session["usuario_nombre"],
        medicamentos=medicamentos
    )

# -------------------------
# GESTION USER
# -------------------------

@usuarios_bp.route(
    "/gestion-user",
    methods=["GET", "POST"]
)
def gestion_user():

    # VALIDAR SESION
    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
        )

    usuario_id = session["usuario_id"]

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    mensaje = None

    error = None

    # -------------------------
    # POST
    # -------------------------

    if request.method == "POST":

        accion = request.form["accion"]

        # -------------------------
        # ACTUALIZAR
        # -------------------------

        if accion == "actualizar":

            nombre = request.form["nombre"].strip()

            documento = request.form["documento"].strip()

            telefono = request.form["telefono"].strip()

            email = request.form["email"].strip()

            direccion = request.form["direccion"].strip()

            # -------------------------
            # VALIDACIONES
            # -------------------------

            # DOCUMENTO

            if not documento.isdigit():

                error = "El documento solo debe contener numeros"

            elif len(documento) < 6 or len(documento) > 10:

                error = "El documento debe tener entre 6 y 10 digitos"

            elif len(set(documento)) == 1:

                error = "El documento no puede tener todos los digitos iguales"

            # VALIDAR DOCUMENTO REPETIDO

            else:

                cursor.execute(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE documento = %s
                    AND id != %s
                    """,
                    (
                        documento,
                        usuario_id
                    )
                )

                documento_existente = cursor.fetchone()

                if documento_existente:

                    error = "El documento ya esta registrado"

            # NOMBRE

            if not error:

                if not nombre.replace(" ", "").isalpha():

                    error = "El nombre solo debe contener letras"

                elif len(nombre) < 3 or len(nombre) > 50:

                    error = "El nombre debe tener entre 3 y 50 caracteres"

                elif len(set(nombre.replace(" ", "").lower())) == 1:

                    error = "El nombre no puede contener una misma cadena repetida"

            # TELEFONO

            if not error:

                if not telefono.isdigit():

                    error = "El telefono solo debe contener numeros"

                elif len(telefono) != 10:

                    error = "El telefono debe tener exactamente 10 digitos"

                elif len(set(telefono)) == 1:

                    error = "El telefono no puede tener todos los digitos iguales"

            # EMAIL

            if not error:

                dominios_validos = [
                    "gmail.com",
                    "outlook.com",
                    "hotmail.com",
                    "yahoo.com"
                ]

                if "@" not in email:

                    error = "El email debe contener @"

                else:

                    dominio = email.split("@")[-1]

                    if dominio not in dominios_validos:

                        error = "Dominio de email no valido"

                    elif len(email) < 10:

                        error = "El email debe tener al menos 10 caracteres"

            # DIRECCION

            if not error:

                if len(set(direccion.replace(" ", "").lower())) == 1:

                    error = "La direccion no puede tener todos los caracteres iguales"

                elif len(direccion) < 10:

                    error = "La direccion debe tener al menos 10 caracteres"

            # -------------------------
            # SI HAY ERROR
            # -------------------------

            if error:

                # OBTENER USUARIO

                cursor.execute(
                    """
                    SELECT *
                    FROM usuarios
                    WHERE id = %s
                    """,
                    (usuario_id,)
                )

                usuario = cursor.fetchone()

                # SOLICITUDES

                cursor.execute(
                    """
                    SELECT
                        medicamentos.nombre_medicamento AS nombre,
                        solicitudes.tipo_entrega,
                        solicitudes.fecha_solicitud,
                        solicitudes.fecha_entrega

                    FROM solicitudes

                    INNER JOIN medicamentos
                        ON solicitudes.medicamento_id = medicamentos.id

                    WHERE solicitudes.persona_id = %s
                    """,
                    (usuario_id,)
                )

                solicitudes = cursor.fetchall()

                conexion.close()

                return render_template(
                    "usuarios-html/crud/gestion_user.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error=error
                )

            # -------------------------
            # ACTUALIZAR DATOS
            # -------------------------

            cursor.execute(
                """
                UPDATE usuarios
                SET
                    nombre = %s,
                    documento = %s,
                    telefono = %s,
                    email = %s,
                    direccion = %s
                WHERE id = %s
                """,
                (
                    nombre,
                    documento,
                    telefono,
                    email,
                    direccion,
                    usuario_id
                )
            )

            conexion.commit()

            mensaje = "Datos actualizados correctamente"

        # -------------------------
        # ELIMINAR
        # -------------------------

        elif accion == "eliminar":

            pin = request.form["pin"]

            cursor.execute(
                """
                SELECT *
                FROM usuarios
                WHERE id = %s AND pin = %s
                """,
                (
                    usuario_id,
                    pin
                )
            )

            usuario = cursor.fetchone()

            if usuario:

                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id = %s
                    """,
                    (usuario_id,)
                )

                conexion.commit()

                conexion.close()

                session.clear()

                return redirect(
                    url_for("usuarios.login_user")
                )

            else:

                # RECARGAR DATOS

                cursor.execute(
                    """
                    SELECT *
                    FROM usuarios
                    WHERE id = %s
                    """,
                    (usuario_id,)
                )

                usuario = cursor.fetchone()

                # SOLICITUDES

                cursor.execute(
                    """
                    SELECT
                        medicamentos.nombre_medicamento AS nombre,
                        solicitudes.tipo_entrega,
                        solicitudes.fecha_solicitud,
                        solicitudes.fecha_entrega

                    FROM solicitudes

                    INNER JOIN medicamentos
                        ON solicitudes.medicamento_id = medicamentos.id

                    WHERE solicitudes.persona_id = %s
                    """,
                    (usuario_id,)
                )

                solicitudes = cursor.fetchall()

                conexion.close()

                return render_template(
                    "usuarios-html/crud/gestion_user.html",
                    usuario=usuario,
                    solicitudes=solicitudes,
                    error_delete="PIN incorrecto"
                )

    # -------------------------
    # OBTENER USUARIO
    # -------------------------

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE id = %s
        """,
        (usuario_id,)
    )

    usuario = cursor.fetchone()

    # -------------------------
    # SOLICITUDES
    # -------------------------

    cursor.execute(
        """
        SELECT
            medicamentos.nombre_medicamento AS nombre,
            solicitudes.tipo_entrega,
            solicitudes.fecha_solicitud,
            solicitudes.fecha_entrega

        FROM solicitudes

        INNER JOIN medicamentos
            ON solicitudes.medicamento_id = medicamentos.id

        WHERE solicitudes.persona_id = %s
        """,
        (usuario_id,)
    )

    solicitudes = cursor.fetchall()

    conexion.close()

    return render_template(
        "usuarios-html/crud/gestion_user.html",
        usuario=usuario,
        solicitudes=solicitudes,
        mensaje=mensaje,
        error=error
    )


# -----------------------------------
# VER MEDICAMENTO USER
# -----------------------------------

@usuarios_bp.route("/ver-medicamento-user/<int:id>")
def ver_medicamento_user(id):

    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
        )

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT * FROM medicamentos
        WHERE id = %s
        """,
        (id,)
    )

    medicamento = cursor.fetchone()

    conexion.close()

    if not medicamento:

        return "Medicamento no encontrado"

    return render_template(
        "usuarios-html/ver_medicamento_user.html",
        medicamento=medicamento
    )


# -----------------------------------
# ENVIO USER
# -----------------------------------

@usuarios_bp.route("/envio-user")
def envio_user():

    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
        )

    medicamento = request.args.get(
        "medicamento"
    )

    tipo_entrega = request.args.get(
        "tipo_entrega"
    )

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY id ASC
        LIMIT 4
        """
    )

    fechas = cursor.fetchall()

    conexion.close()

    return render_template(
        "usuarios-html/envio_medicamento_user.html",
        medicamento=medicamento,
        tipo_entrega=tipo_entrega,
        fechas=fechas
    )

# -----------------------------------
# GUARDAR SOLICITUD USER
# -----------------------------------

@usuarios_bp.route(
    "/guardar-solicitud-user",
    methods=["POST"]
)
def guardar_solicitud_user():

    # VALIDAR SESION

    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
        )

    usuario_id = session["usuario_id"]

    # RECIBIR DATOS

    medicamento_nombre = request.form["medicamento"]

    tipo_entrega = request.form["tipo_entrega"]

    fecha_entrega = request.form["fecha_entrega"]

    # CONEXION

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
            "usuarios-html/envio_medicamento_user.html",
            mensaje="Selecciona una fecha para la entrega",
            medicamento=medicamento_nombre,
            tipo_entrega=tipo_entrega,
            fechas=fechas
        )

    # OBTENER FECHAS GLOBALES

    cursor.execute(
        """
        SELECT *
        FROM fechas_disponibles
        ORDER BY fecha ASC
        LIMIT 4
        """
    )

    fechas = cursor.fetchall()

    # BUSCAR MEDICAMENTO

    cursor.execute(
        """
        SELECT *
        FROM medicamentos
        WHERE nombre_medicamento = %s
        """,
        (medicamento_nombre,)
    )

    medicamento = cursor.fetchone()

    # VALIDAR MEDICAMENTO

    if not medicamento:

        conexion.close()

        return "Medicamento no encontrado"

    # VALIDAR STOCK

    if medicamento["stock"] <= 0:

        conexion.close()

        return render_template(
            "usuarios-html/envio_medicamento_user.html",
            mensaje="No hay stock disponible",
            medicamento=medicamento_nombre,
            tipo_entrega=tipo_entrega,
            fechas=fechas
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
            usuario_id,
            "usuario",
            medicamento["id"],
            tipo_entrega,
            fecha_entrega
        )
    )

    solicitud_id = cursor.lastrowid

    # CREAR FACTURA

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
            usuario_id,
            "usuario",
            medicamento["id"],
            solicitud_id,
            0,
            0,
            "eps"
        )
    )

    conexion.commit()

    conexion.close()

    # RETORNAR HTML

    return render_template(
        "usuarios-html/envio_medicamento_user.html",
        mensaje="Solicitud realizada exitosamente",
        medicamento=medicamento_nombre,
        tipo_entrega=tipo_entrega,
        fechas=fechas,
        mostrar_factura=True,
        solicitud_id=solicitud_id
    )


# -----------------------------------
# GENERAR FACTURA USER
# -----------------------------------

@usuarios_bp.route(
    "/generar-factura-user/<int:solicitud_id>"
)
def generar_factura_user(solicitud_id):

    if "usuario_id" not in session:

        return redirect(
            url_for("usuarios.login_user")
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

            usuarios.nombre,
            usuarios.documento,
            usuarios.email,
            usuarios.telefono

        FROM solicitudes

        INNER JOIN medicamentos
            ON solicitudes.medicamento_id = medicamentos.id

        INNER JOIN usuarios
            ON solicitudes.persona_id = usuarios.id

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

    width, height = letter

    pdf.setFont("Helvetica-Bold", 22)

    pdf.drawString(
        180,
        750,
        "FACTURA EPS"
    )

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        50,
        700,
        "DATOS DEL USUARIO"
    )

    pdf.setFont("Helvetica", 12)

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

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        50,
        570,
        "MEDICAMENTO"
    )

    pdf.setFont("Helvetica", 12)

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

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        50,
        460,
        "FECHAS"
    )

    pdf.setFont("Helvetica", 12)

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

    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawString(
        50,
        360,
        "TOTAL PAGADO: $0 (PBS)"
    )

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        50,
        300,
        "Gracias por utilizar CatalogoEPS."
    )

    pdf.drawString(
        50,
        280,
        "Tu medicamento sera entregado en la fecha seleccionada."
    )

    pdf.showPage()

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="factura_eps.pdf",
        mimetype="application/pdf"
    )

# -----------------------------------
# VALIDAR USUARIO PARA CAMBIAR PIN
# -----------------------------------

@usuarios_bp.route(
    "/modificar-pin-validar-user",
    methods=["GET", "POST"]
)
def modificar_pin_validar_user():

    # -------------------------
    # MOSTRAR FORMULARIO
    # -------------------------

    if request.method == "GET":

        return render_template(
            "usuarios-html/crud/modificar_pin_validar_user.html"
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
    # VALIDAR USUARIO
    # -------------------------

    cursor.execute(
        """
        SELECT *
        FROM usuarios
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

    usuario = cursor.fetchone()

    conexion.close()

    # -------------------------
    # USUARIO NO EXISTE
    # -------------------------

    if not usuario:

        return render_template(
            "usuarios-html/crud/modificar_pin_validar_user.html",
            error="Los datos no coinciden"
        )

    # -------------------------
    # GUARDAR ID TEMPORAL
    # -------------------------

    session["recuperar_usuario_id"] = usuario["id"]

    session["recuperar_usuario_nombre"] = usuario["nombre"]

    # -------------------------
    # REDIRECCION
    # -------------------------

    return redirect(
        url_for("usuarios.modificar_pin_user")
    )

# -----------------------------------
# MODIFICAR PIN USER
# -----------------------------------

@usuarios_bp.route(
    "/modificar-pin-user",
    methods=["GET", "POST"]
)
def modificar_pin_user():

    # VALIDAR SESION TEMPORAL
    if "recuperar_usuario_id" not in session:

        return redirect(
            url_for("usuarios.modificar_pin_validar_user")
        )

    # MOSTRAR HTML
    if request.method == "GET":

        return render_template(
            "usuarios-html/crud/modificar_pin_user.html",
            usuario=session["recuperar_usuario_nombre"]
        )

    # RECIBIR DATOS
    pin = request.form["pin"]

    confirmar_pin = request.form["confirmar_pin"]

    # VALIDAR PINS
    if pin != confirmar_pin:

        return render_template(
            "usuarios-html/crud/modificar_pin_user.html",
            usuario=session["recuperar_usuario_nombre"],
            error="Los PIN no coinciden"
        )
        
    if not pin.isdigit():
    
        return render_template(
            "usuarios-html/crud/modificar_pin_user.html",
            usuario=session["recuperar_usuario_nombre"],
            error="El PIN debe contener solo numeros"
        )
        
    if len(pin) != 4:
        
        return render_template(
            "usuarios-html/crud/modificar_pin_user.html",
            usuario=session["recuperar_usuario_nombre"],
            error="El PIN debe tener 4 digitos"
        )

    # ACTUALIZAR PIN
    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE usuarios
        SET pin = %s
        WHERE id = %s
        """,
        (
            pin,
            session["recuperar_usuario_id"]
        )
    )

    conexion.commit()

    conexion.close()

    # LIMPIAR SESION TEMPORAL
    session.pop("recuperar_usuario_id", None)

    session.pop("recuperar_usuario_nombre", None)

    # REDIRECCION LOGIN
    return redirect(
        url_for("usuarios.login_user")
    )


# -----------------------------------
# LOGOUT USER
# -----------------------------------

@usuarios_bp.route("/logout-user")
def logout_user():

    session.clear()

    return redirect(
        url_for("usuarios.login_user")
    )

