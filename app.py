from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)

# clave para manejar sesiones
app.secret_key = "catalogo_eps_clave_secreta"


# ---------------------------
# FUNCIÓN DE CONEXIÓN
# ---------------------------

def obtener_conexion():
    return pymysql.connect(
        host="localhost",
        user="app_user",
        password="123456",
        database="catalogo_eps",
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------------------
# CREAR USUARIO
# ---------------------------

@app.route("/crear_usuario", methods=["GET", "POST"])
def crear_usuario():

    if request.method == "GET":
        return render_template("crud/crear_usuario.html")

    # ---------------------------
    # OBTENER DATOS
    # ---------------------------

    documento = request.form["documento"]
    nombre = request.form["nombre"]
    pin = request.form["pin"]
    telefono = request.form["telefono"]
    email = request.form["email"]
    direccion = request.form["direccion"]

    # ---------------------------
    # VALIDACIONES
    # ---------------------------

    # Documento
    if not documento.isdigit():
        return render_template("crud/crear_usuario.html", error="El documento solo debe contener números")

    if len(documento) < 6 or len(documento) > 10:
        return render_template("crud/crear_usuario.html", error="El documento debe tener entre 6 y 10 dígitos")

    if len(set(documento)) == 1:
        return render_template("crud/crear_usuario.html", error="El documento no puede tener todos los dígitos iguales")

    # Nombre
    if not nombre.replace(" ", "").isalpha():
        return render_template("crud/crear_usuario.html", error="El nombre solo debe contener letras")

    if len(nombre) < 3 or len(nombre) > 50:
        return render_template("crud/crear_usuario.html", error="El nombre debe tener entre 3 y 50 caracteres")

    # PIN
    if not pin.isdigit():
        return render_template("crud/crear_usuario.html", error="El PIN solo debe contener números")

    if len(pin) != 4:
        return render_template("crud/crear_usuario.html", error="El PIN debe tener exactamente 4 dígitos")

    # Teléfono
    if not telefono.isdigit():
        return render_template("crud/crear_usuario.html", error="El teléfono solo debe contener números")

    if len(telefono) != 10:
        return render_template("crud/crear_usuario.html", error="El teléfono debe tener 10 dígitos")

    if len(set(telefono)) == 1:
        return render_template("crud/crear_usuario.html", error="El teléfono no puede tener todos los dígitos iguales")

    # Email
    dominios_validos = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]

    if "@" not in email:
        return render_template("crud/crear_usuario.html", error="El email debe contener @")

    dominio = email.split("@")[-1]

    if dominio not in dominios_validos:
        return render_template("crud/crear_usuario.html", error="Dominio de email no válido")

    if len(email) < 10:
        return render_template("crud/crear_usuario.html", error="El email debe tener al menos 10 caracteres")

    # Dirección
    if len(set(direccion)) == 1:
        return render_template("crud/crear_usuario.html", error="La direccion no puede tener todos los dígitos iguales")

    if len(direccion) < 10:
        return render_template("crud/crear_usuario.html", error="La dirección debe tener al menos 10 caracteres")

    # ---------------------------
    # BASE DE DATOS
    # ---------------------------

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Verificar documento único
    cursor.execute("SELECT * FROM usuarios WHERE documento = %s", (documento,))
    existente = cursor.fetchone()

    if existente:
        conexion.close()
        return render_template("crud/crear_usuario.html", error="El documento ya está registrado")
    
    #Verificar combinación similar (nombre + teléfono + email)
    cursor.execute("""
    SELECT * FROM usuarios 
    WHERE nombre = %s AND telefono = %s AND email = %s
    """, (nombre, telefono, email))

    duplicado = cursor.fetchone()

    if duplicado:
        conexion.close()
        return render_template(
            "crud/crear_usuario.html",
            error="Ya existe un usuario con datos muy similares"
        )

    # Insertar usuario
    cursor.execute("""
        INSERT INTO usuarios (documento, nombre, telefono, email, direccion, pin)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (documento, nombre, telefono, email, direccion, pin))

    conexion.commit()
    conexion.close()

    return redirect("/")

# ---------------------------
# MODIFICAR PIN VALIDAR
# ---------------------------

@app.route("/modificar_pin_validar", methods=["GET", "POST"])
def modificar_pin_validar():

    if request.method == "GET":
        session["intentos"] = 5
        return render_template("crud/modificar_pin_validar.html")

    # ---------------------------
    # CONTROL DE INTENTOS
    # ---------------------------

    if "intentos" not in session:
        session["intentos"] = 5

    intentos = session["intentos"]

    if intentos <= 0:
        return render_template("crud/modificar_pin_validar.html", error="Has agotado todos los intentos")

    # ---------------------------
    # DATOS
    # ---------------------------

    nombre = request.form["nombre"]
    documento = request.form["documento"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    # ---------------------------
    # VALIDACIONES
    # ---------------------------

    # Nombre
    if not nombre.replace(" ", "").isalpha() or len(nombre) < 3 or len(nombre) > 50:
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"El nombre está incorrecto. Te quedan {session['intentos']} intentos")

    # Documento
    if (not documento.isdigit() or
        len(documento) < 6 or len(documento) > 10 or
        len(set(documento)) == 1):
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"El documento está incorrecto. Te quedan {session['intentos']} intentos")

    # Email
    dominios_validos = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]

    if "@" not in email or len(email) < 10:
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"El email está incorrecto. Te quedan {session['intentos']} intentos")

    dominio = email.split("@")[-1]

    if dominio not in dominios_validos:
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"El email está incorrecto. Te quedan {session['intentos']} intentos")

    # Teléfono
    if (not telefono.isdigit() or
        len(telefono) != 10 or
        len(set(telefono)) == 1):
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"El teléfono está incorrecto. Te quedan {session['intentos']} intentos")

    # ---------------------------
    # VERIFICAR EN BD
    # ---------------------------

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT * FROM usuarios 
        WHERE documento = %s AND nombre = %s AND email = %s AND telefono = %s
    """, (documento, nombre, email, telefono))

    usuario = cursor.fetchone()
    conexion.close()

    if not usuario:
        session["intentos"] -= 1
        return render_template("crud/modificar_pin_validar.html", error=f"Los datos no coinciden. Te quedan {session['intentos']} intentos")

    # ---------------------------
    # ACCESO CORRECTO
    # ---------------------------

    session["usuario_recuperacion"] = usuario["id"]

    return redirect("/modificar_pin")

# ---------------------------
# MODIFICAR PIN (UPDATE)
# ---------------------------

@app.route("/modificar_pin", methods=["GET", "POST"])
def modificar_pin():

    # Seguridad: solo entra si viene del paso anterior
    if "usuario_recuperacion" not in session:
        return redirect("/")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener datos del usuario
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (session["usuario_recuperacion"],))
    usuario = cursor.fetchone()

    if request.method == "GET":
        conexion.close()
        return render_template("crud/modificar_pin.html", usuario=usuario["nombre"])

    # ---------------------------
    # DATOS
    # ---------------------------

    pin = request.form["pin"]
    confirmar_pin = request.form["confirmar_pin"]

    # ---------------------------
    # VALIDACIONES
    # ---------------------------

    if not pin.isdigit():
        conexion.close()
        return render_template("crud/modificar_pin.html", usuario=usuario["nombre"], error="El PIN solo debe contener números")

    if len(pin) != 4:
        conexion.close()
        return render_template("crud/modificar_pin.html", usuario=usuario["nombre"], error="El PIN debe tener exactamente 4 dígitos")

    if pin != confirmar_pin:
        conexion.close()
        return render_template("crud/modificar_pin.html", usuario=usuario["nombre"], error="Tu confirmación no coincide con el PIN")

    # ---------------------------
    # ACTUALIZAR BD
    # ---------------------------

    cursor.execute("UPDATE usuarios SET pin = %s WHERE id = %s", (pin, usuario["id"]))

    conexion.commit()
    conexion.close()

    # limpiar sesión de recuperación
    session.pop("usuario_recuperacion", None)

    return redirect("/")

# ---------------------------
# GESTION USUARIO (READ + UPDATE + DELETE)
# ---------------------------

@app.route("/gestion_usuario", methods=["GET", "POST"])
def gestion_usuario():

    if "usuario_id" not in session:
        return redirect("/")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = %s",(session["usuario_id"],))
    usuario = cursor.fetchone()

    # 🔥 OBTENER SOLICITUDES SIEMPRE (para no romper renders)
    cursor.execute("""
        SELECT 
            s.tipo_entrega,
            s.fecha_solicitud,
            s.fecha_entrega,
            m.nombre
        FROM solicitudes s
        JOIN medicamentos m ON s.medicamento_id = m.id
        WHERE s.usuario_id = %s
        ORDER BY s.fecha_solicitud DESC
    """, (session["usuario_id"],))

    solicitudes = cursor.fetchall()

    # ---------------------------
    # GET (mostrar datos)
    # ---------------------------

    if request.method == "GET":
        conexion.close()
        return render_template(
            "crud/gestion_usuario.html",
            usuario=usuario,
            solicitudes=solicitudes   # 🔥 IMPORTANTE
        )

    accion = request.form.get("accion")

    # ---------------------------
    # UPDATE
    # ---------------------------

    if accion == "actualizar":

        nombre = request.form["nombre"]
        documento = request.form["documento"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # 🔥 SIEMPRE TRAER SOLICITUDES (para no romper render en errores)
        cursor.execute("""
            SELECT 
                s.tipo_entrega,
                s.fecha_solicitud,
                s.fecha_entrega,
                m.nombre
            FROM solicitudes s
            JOIN medicamentos m ON s.medicamento_id = m.id
            WHERE s.usuario_id = %s
            ORDER BY s.fecha_solicitud DESC
        """, (session["usuario_id"],))

        solicitudes = cursor.fetchall()

        # 🔥 USUARIO TEMPORAL (estructura compatible con template)
        usuario_temp = {
            "id": session["usuario_id"],
            "nombre": nombre,
            "documento": documento,
            "email": email,
            "telefono": telefono,
            "direccion": direccion
        }

        # ---------------------------
        # VALIDACIONES
        # ---------------------------

        if not nombre.replace(" ", "").isalpha() or len(nombre) < 3 or len(nombre) > 50:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Nombre inválido")

        if (not documento.isdigit() or
            len(documento) < 6 or len(documento) > 10 or
            len(set(documento)) == 1):
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Documento inválido")

        # DOCUMENTO ÚNICO
        cursor.execute("""
            SELECT * FROM usuarios 
            WHERE documento=%s AND id != %s
        """, (documento, session["usuario_id"]))

        existe_doc = cursor.fetchone()

        if existe_doc:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="El documento ya está en uso")

        # EMAIL
        dominios_validos = ["gmail.com","outlook.com","hotmail.com","yahoo.com"]

        if "@" not in email or len(email) < 10:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Email inválido")

        dominio = email.split("@")[-1]

        if dominio not in dominios_validos:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Dominio de email inválido")

        # TELÉFONO
        if (not telefono.isdigit() or
            len(telefono) != 10 or
            len(set(telefono)) == 1):
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Teléfono inválido")

        # DIRECCIÓN
        if len(direccion) < 6:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                usuario=usuario_temp,
                solicitudes=solicitudes,
                error="Dirección inválida")

        # ---------------------------
        # UPDATE REAL
        # ---------------------------

        cursor.execute("""
            UPDATE usuarios 
            SET nombre=%s, documento=%s, email=%s, telefono=%s, direccion=%s
            WHERE id=%s
        """, (nombre, documento, email, telefono, direccion, session["usuario_id"]))

        conexion.commit()

        # 🔥 ACTUALIZAR SESIÓN
        session["usuario"] = nombre

        # 🔥 TRAER DATOS ACTUALIZADOS
        cursor.execute("SELECT * FROM usuarios WHERE id=%s", (session["usuario_id"],))
        usuario_actualizado = cursor.fetchone()

        conexion.close()

        return render_template("crud/gestion_usuario.html",
            usuario=usuario_actualizado,
            solicitudes=solicitudes,
            mensaje="Datos actualizados correctamente")

    # ---------------------------
    # DELETE
    # ---------------------------

    elif accion == "eliminar":

        pin = request.form["pin"]

        if not pin.isdigit() or len(pin) != 4:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                                usuario=usuario,
                                solicitudes=solicitudes,
                                error_delete="PIN inválido")

        if pin != usuario["pin"]:
            conexion.close()
            return render_template("crud/gestion_usuario.html",
                                usuario=usuario,
                                solicitudes=solicitudes,
                                error_delete="PIN incorrecto")

        cursor.execute("DELETE FROM usuarios WHERE id=%s",
                    (usuario["id"],))

        conexion.commit()
        conexion.close()

        session.clear()

        return redirect("/")
# ---------------------------
# PAGINA DE LOGIN
# ---------------------------

@app.route("/")
def inicio():
    return render_template("login.html")


# ---------------------------
# LOGIN 
# ---------------------------

@app.route("/login", methods=["POST"])
def login():

    documento = request.form["documento"]
    pin = request.form["pin"]

    # ---------------------------
    # VALIDACIONES BÁSICAS
    # ---------------------------

    if not documento.isdigit():
        return render_template("login.html", error="El documento solo debe contener números")

    if not pin.isdigit():
        return render_template("login.html", error="El PIN solo debe contener números")

    if len(documento) < 6 or len(documento) > 10:
        return render_template("login.html", error="El documento debe tener entre 6 y 10 dígitos")

    if len(pin) != 4:
        return render_template("login.html", error="El PIN debe tener exactamente 4 dígitos")

    # ---------------------------
    # CONSULTA A LA BD
    # ---------------------------

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE documento = %s", (documento,))
    usuario = cursor.fetchone()


    conexion.close()

    # ---------------------------
    # VALIDACIÓN DE DATOS
    # ---------------------------

    if not usuario:
        return render_template("login.html", error="Documento no registrado")

    if usuario["pin"] != pin:
        return render_template("login.html", error="PIN incorrecto")

    # ---------------------------
    # LOGIN EXITOSO
    # ---------------------------

    session["usuario"] = usuario["nombre"]
    session["usuario_id"] = usuario["id"]

    return redirect("/catalogo")


# ---------------------------
# CATALOGO
# ---------------------------

@app.route("/catalogo")
def catalogo():

    if "usuario" not in session:
        return redirect("/")

    usuario = session["usuario"]

    return render_template("catalogo.html", usuario=usuario)


# ---------------------------
# INGRESO A MEDICAMENTO
# ---------------------------

@app.route("/medicamento/<nombre>")
def ver_medicamento(nombre):

    if "usuario" not in session:
        return redirect("/")

    return render_template(f"medicamento/{nombre}.html")


# ---------------------------
# INGRESO A ENVIO
# ---------------------------

@app.route("/envio")
def envio():

    if "usuario" not in session:
        return redirect("/")

    medicamento = request.args.get("medicamento")
    tipo_entrega = request.args.get("tipo_entrega")

    return render_template(
        "envio_medicamento.html",
        medicamento=medicamento,
        tipo_entrega=tipo_entrega
    )


# ---------------------------
# SOLICITUDES
# ---------------------------

@app.route("/guardar_solicitud", methods=["POST"])
def guardar_solicitud():

    if "usuario_id" not in session:
        return redirect("/")

    usuario_id = session["usuario_id"]
    medicamento_nombre = request.form["medicamento"]
    tipo_entrega = request.form["tipo_entrega"]
    fecha_entrega = request.form["fecha_entrega"]

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener ID del medicamento por nombre
    cursor.execute("SELECT id FROM medicamentos WHERE nombre = %s", (medicamento_nombre,))
    medicamento = cursor.fetchone()

    if not medicamento:
        conexion.close()
        return "Medicamento no encontrado"

    medicamento_id = medicamento["id"]

    # Insertar solicitud en la base de datos
    cursor.execute("""
        INSERT INTO solicitudes (usuario_id, medicamento_id, tipo_entrega, fecha_entrega)
        VALUES (%s, %s, %s, %s)
    """, (usuario_id, medicamento_id, tipo_entrega, fecha_entrega))

    conexion.commit()
    conexion.close()

    return render_template(
        "envio_medicamento.html",
        mensaje="Pedido realizado exitosamente",
        medicamento=medicamento_nombre,
        tipo_entrega=tipo_entrega
    )


# ---------------------------
# CERRAR SESION
# ---------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)