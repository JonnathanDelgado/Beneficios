from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import Verificacion as verif
from sheet import buscar_cliente_por_dni
from db_auth import verify_login
from db_auth import get_all_partners
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd  # <-- NUEVO (pip install pandas openpyxl)

# db_gpon
app = Flask(__name__)
app.secret_key = "dev"  # Cambia esto en producción

# Ahora sí podemos usar app.static_folder
PREVIEW_DIR = os.path.join(app.static_folder, 'tmp')
os.makedirs(PREVIEW_DIR, exist_ok=True)

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
        idcliente = documento
        trabajador = buscar_cliente_por_dni(idcliente)
        if trabajador:
            booleano, nombre_cliente = verif.verificar_trabajador_3_meses(trabajador)
            if booleano:
                return {"nombre_cliente": nombre_cliente, "documento": documento, "estado": "APROBADO"}
            else: return {"nombre_cliente": nombre_cliente, "documento": documento, "estado": "DENEGADO"}
        else:
            return {"nombre_cliente": "DESCONOCIDO", "documento": documento, "estado": "DENEGADO"}

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
                if username.lower() == "gponadmin":
                    return redirect(url_for("partners"))
                
                flash(f"Bienvenido, {name}.", "info")
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
    preview_url = session.pop("preview_url", None)  # <-- NUEVO
    return render_template("index.html", preview_url=preview_url)  # <-- CAMBIO

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

    # Validar extensión
    if not _allowed_excel(f.filename):
        flash("Extensión no permitida. Usa .xlsx, .xls o .csv.", "error")
        return redirect(url_for("index"))
    
    # Carpeta por usuario (según el nombre guardado en la sesión)
    user_name = session.get("user", "user")
    user_slug = _slugify_user(user_name)
    user_dir = os.path.join(app.config["BENEFICIARIOS_DIR"], user_slug)
    os.makedirs(user_dir, exist_ok=True)

    # Renombrar por fecha/hora actual y conservar extensión
    safe_original = secure_filename(f.filename)
    ext = "." + safe_original.rsplit(".", 1)[1].lower()
    new_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ext

    save_path = os.path.join(user_dir, new_name)
    f.save(save_path)

        # === NUEVO: Generar HTML de vista previa ===
    try:
        if ext == ".csv":
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)  # Primera hoja por defecto

        df_preview = df.head(30)  # limitar filas para rendimiento
        table_html = df_preview.to_html(index=False, classes="excel-table")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        preview_filename = f"preview_{user_slug}_{ts}.html"
        preview_path = os.path.join(PREVIEW_DIR, preview_filename)

        with open(preview_path, "w", encoding="utf-8") as fh:
            rendered_html = render_template("preview_template.html", table_html=table_html)
            fh.write(rendered_html)


        # Guardar URL en sesión para que index la lea
        session["preview_url"] = url_for('static', filename=f'tmp/{preview_filename}')

    except Exception as e:
        print("[upload_beneficiarios] Error generando preview:", e)
        flash("Archivo subido, pero no se pudo generar la vista previa.", "error")
    
    flash("Archivo subido exitosamente", "success")
    return redirect(url_for("index"))

@app.route("/partners", methods=["GET"])
@login_required
def partners():
    # obtner partners de la base de datos
    global FAKE_PARTNERS
    FAKE_PARTNERS = get_all_partners()
    return render_template("partners.html", partners=FAKE_PARTNERS)

@app.route("/consultar_partner", methods=["POST"])
@login_required
def consultar_partner():
    partner_id = request.form.get("partner_id", "").strip()
    if not partner_id:
        flash("Debes seleccionar un partner.", "error")
        return redirect(url_for("partners"))

    # Aquí harás la lógica de consulta real por partner_id
    # Por ahora, solo confirmamos
    sel = next((p for p in FAKE_PARTNERS if p["id"] == partner_id), None)
    if not sel:
        flash("El partner seleccionado no existe.", "error")
        return redirect(url_for("partners"))

    flash(f"Consulta realizada para: {sel['nombre']}", "success")
    return redirect(url_for("partners"))


if __name__ == "__main__":
    app.run(debug=True)
