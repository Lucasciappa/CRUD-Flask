from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)

mysql = MySQL()
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "bacus"

mysql.init_app(app)

#Referencia a mi archivos
CARPETA = os.path.join("uploads")
app.config["CARPETA"] = CARPETA

app.secret_key = "miClave"


@app.route("/")
def index():
    sql  = "SELECT * FROM empleados;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)

    return render_template("bacus/index.html", empleados = empleados)


@app.route("/create")
def create():

    return render_template("bacus/create.html")

@app.route("/store", methods=["POST"])
def storage():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files["txtFoto"]

    # Validacion de datos
    if _nombre == "" or _correo == "" or _foto == "":
        flash("Faltan ingresar datos!") #TO-DO
        return redirect(url_for("create"))

    ahora = datetime.now()
    tiempo = ahora.strftime("%Y%H%M%S")
    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    sql  = "INSERT INTO `empleados` (`nombre`, `email`, `foto`) VALUES (%s, %s, %s);"
    datos= (_nombre, _correo, nuevoNombreFoto)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    return redirect("/")

@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('SELECT foto FROM empleados WHERE id = %s', id)
    fila = cursor.fetchone()
    os.remove(os.path.join(app.config["CARPETA"], fila[0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s", id)
    conn.commit()
    return redirect("/")



@app.route("/edit/<int:id>")
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", id)
    empleado = cursor.fetchone()

    return render_template("bacus/edit.html", empleado = empleado)

@app.route("/update", methods=["POST"])
def update():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files["txtFoto"]
    id = request.form["txtId"]

    sql = "UPDATE empleados SET nombre = %s, email = %s WHERE id = %s;"
    datos = (_nombre, _correo, id )
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)

    ahora = datetime.now()
    tiempo = ahora.strftime("%Y%H%M%S")
    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)
        cursor.execute('SELECT foto FROM empleados WHERE id = %s', id)
        fila = cursor.fetchone()
        os.remove(os.path.join(app.config["CARPETA"], fila[0]))
        cursor.execute('UPDATE empleados SET foto = %s WHERE id = %s', (nuevoNombreFoto, id))

    conn.commit() # Grabo las modif en mi BD
    
    return redirect("/")


@app.route("/uploads/<nombreFoto>")
def uploads(nombreFoto):
    return send_from_directory(app.config["CARPETA"], nombreFoto)

if __name__ == "__main__":
    app.run(debug=True)
