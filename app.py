# app.py

from flask import Flask, render_template
from config import Config

# IMPORTAR BLUEPRINTS
from routes.usuarios import usuarios_bp
from routes.clientes import clientes_bp
from routes.empleados import empleados_bp


app = Flask(__name__)

# -----------------------------------
# INICIO
# -----------------------------------

@app.route("/")
def inicio():

    return render_template(
        "inicio.html"
    )

app.config.from_object(Config)

# REGISTRAR MÓDULOS
app.register_blueprint(usuarios_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(empleados_bp)


if __name__ == "__main__":        
    app.run(debug=True) 
    

#VERIFICAR INCOHERENCIA ENTRE FECHAS DE "CLIENTE" Y "EMPLEADO" AL MOMENTO DE INTENTAR MODIFICAR:

#mirar chatgpt(ultimo mensaje) y plantear lo siguiente:



#VERIFICAR PROBLEMA AL MOMENTO DE INTENTR INGRESAR A "gestion_employ.html"


# VERIFICAR ERRORES EN MODULO "empleados" Y TERMINARLO


#detalles

#mostrar precio de "medicamento" en card de solicitudes

#agregar responsive a "envio_medicamento_employ.css"