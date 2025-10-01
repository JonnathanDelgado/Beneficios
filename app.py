from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import Verificacion as verif
from db_auth import verify_login
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# db_gpon
app = Flask(__name__)
app.secret_key = "dev"  # Cambia esto en producción
# Carpeta destino en PythonAnywhere (se expande a /home/GPON2/Beneficiarios)
app.config["BENEFICIARIOS_DIR"] = os.path.expanduser("~/Beneficiarios")
os.makedirs(app.config["BENEFICIARIOS_DIR"], exist_ok=True)

# Tamaño máximo del archivo: 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

# Extensiones permitidas
EXCEL_EXTS = {"xlsx", "xls", "csv"}

def _allowed_excel(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXCEL_EXTS

def _slugify_user(u: str) -> str:
    # convierte a nombre seguro de archivo
    base = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in (u or "user"))
    return base.strip("_") or "user"

USERS = None  # autenticación delegada a verify_login (MySQL + SSH)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper

def consulta_principal(documento: str, tipo: str, select_documento: str):
    if tipo == "cliente":
        if select_documento == "DNI":
            idcliente = documento
        else:
            idcliente = documento.zfill(12)  # Rellenar con ceros a la izquierda para Carnet de Extranjería
        Dpto = "Lima"
        data = verif.consumir_api_plataformaweb(idcliente, Dpto)
        if not data:
            return {"nombre_cliente": "—", "documento": documento, "estado": "ERROR", "mensaje": "No se obtuvo respuesta de la API"}
        resultado = verif.extraer_datos(data)
        cliente_antiguo = verif.obtener_cliente_mas_antiguo(resultado)
        booleano, nombre_cliente = verif.verificar_cliente_3_meses(cliente_antiguo)
        if booleano:
            return {"nombre_cliente": nombre_cliente, "documento": documento, "estado": "APROBADO"}
        else:
            return {"nombre_cliente": nombre_cliente, "documento": documento, "estado": "DENEGADO"}
    else:
        return {"nombre_cliente": "Trabajador", "documento": documento, "estado": "falta que nos den la data"}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        nxt = request.form.get("next") or request.args.get("next") or url_for("index")
        try:
            ok, name = verify_login(username, password)
            if ok:
                session["user"] = name  # Guardamos el `name` en la sesión
                flash(f"Bienvenido, {name}.", "success")
                return redirect(nxt)
            else:
                flash("Usuario o contraseña incorrectos.", "error")
        except Exception as e:
            # Registra el error en consola para depurar y muestra mensaje genérico al usuario
            print("[login] Error de verificación:", e)
            flash("No se pudo verificar las credenciales. Intenta de nuevo más tarde.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")

@app.route("/consultar", methods=["POST"])
@login_required
def consultar():
    documento = (request.form.get("documento") or "").strip()
    tipo = request.form.get("tipo") or "cliente"
    select_documento = request.form.get("select_documento")
    if not documento:
        flash("Ingresa un DNI o Carnet de Extranjería.", "error")
        return redirect(url_for("index"))
    resultado = consulta_principal(documento, tipo, select_documento)
    return render_template("resultado.html", data=resultado)

@app.route("/upload_beneficiarios", methods=["POST"])
@login_required
def upload_beneficiarios():
    f = request.files.get("file")
    if not f or f.filename == "":
        flash("No se seleccionó archivo.", "error")
        return redirect(url_for("index"))

    if not _allowed_excel(f.filename):
        flash("Extensión no permitida. Usa .xlsx, .xls o .csv.", "error")
        return redirect(url_for("index"))

    # nombre seguro + extensión
    safe_original = secure_filename(f.filename)
    ext = "." + safe_original.rsplit(".", 1)[1].lower()

    # YYYYMMDD_HHMMSS_usuario.ext
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_slug = _slugify_user(session.get("user"))
    new_name = f"{now_str}_{user_slug}{ext}"

    dest = os.path.join(app.config["BENEFICIARIOS_DIR"], new_name)
    f.save(dest)

    flash(f"Archivo subido como {new_name}.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
