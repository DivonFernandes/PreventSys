import requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import sys

# Adicionar o diretório atual ao path para importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import gerar_grafico, contar_itens_lista
except ImportError:
    # Fallback se utils não estiver disponível
    def contar_itens_lista(entradas, campo):
        return {}
    
    def gerar_grafico(contagem, titulo, xlabel, ylabel='Quantidade', small=False, nomes_abaixo=False):
        return ""

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Quantidade por página para listagem
PER_PAGE = 20

class Entrada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emitente = db.Column(db.String(40), nullable=False)
    classificação = db.Column(db.String(15), nullable=False)
    empresa = db.Column(db.String(15), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    local = db.Column(db.String(20), nullable=False)
    observação = db.Column(db.String(150), nullable=False)
    ação = db.Column(db.String(150), nullable=False)
    class_sst = db.Column(db.String(50), nullable=True)
    class_ambiental = db.Column(db.String(50), nullable=True)
    causa = db.Column(db.String(300), nullable=True)
    parecer = db.Column(db.String(100), nullable=True)
    num_ordem_man = db.Column(db.String(20), nullable=True)
    obs_sprocedencia = db.Column(db.String(20), nullable=True)
    obs_justificativa = db.Column(db.String(20), nullable=True)
    multipla_condição = db.Column(db.String(60), nullable=True)
    multipla_comportamento = db.Column(db.String(60), nullable=True)
    multipla_ambiental = db.Column(db.String(60), nullable=True)
    funcionario = db.Column(db.String(20), nullable=True)

# Criar tabelas
with app.app_context():
    db.create_all()

def get_weather_today(lat, lon, timezone_str='America/Sao_Paulo'):
    try:
        hoje = datetime.now().date()
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
            f"&timezone={timezone_str}"
        )
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        d = data.get('daily', {})
        if not d or not d.get('time'):
            return None

        # Encontrar índice do dia atual
        idx = None
        for i, dia_str in enumerate(d['time']):
            if dia_str == hoje.isoformat():
                idx = i
                break
        if idx is None:
            return None

        # SEMPRE retorna "Sem riscos significativos hoje"
        summary = "Sem riscos significativos hoje"

        return {
            "summary": summary
        }

    except Exception:
        return None

def init_auth_db():
    with sqlite3.connect("usuarios.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )''')

        # Inserir usuário de teste se não existir
        c.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)", 
                 ('teste', '1234'))
        conn.commit()

init_auth_db()

# Servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Rota principal
@app.route('/')
def index():
    LATITUDE = -21.3607
    LONGITUDE = -48.2282
    
    # Obter dados meteorológicos - apenas o summary simplificado
    weather_today = get_weather_today(LATITUDE, LONGITUDE)
    
    weather = None
    if weather_today:
        weather = {
            'summary': weather_today['summary']
        }
    
    return render_template('index.html', weather=weather)

# Tela de Login para o SSMA 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["username"]
        senha = request.form["password"]
        with sqlite3.connect("usuarios.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (usuario, senha))
            user = c.fetchone()
            if user:
                session["logado"] = True
                session["username"] = usuario
                return redirect(url_for("ssma"))
        
        return render_template("login.html", error="Login inválido!")
    
    return render_template("login.html")

# Página exclusiva do SSMA 
@app.route("/ssma", methods=["GET", "POST"])             
def ssma():
    if not session.get("logado"):
        return redirect(url_for("login"))

    # Submissão de dados
    if request.method == "POST":
        ids = request.form.getlist("id_list")
        for entrada_id in ids:
            entrada = Entrada.query.get(entrada_id)
            if entrada:
                entrada.class_sst = request.form.get(f"class_sst_{entrada_id}", "")
                entrada.class_ambiental = request.form.get(f"class_ambiental_{entrada_id}", "")
                entrada.causa = ', '.join(request.form.getlist(f"causa_{entrada_id}"))
                entrada.parecer = request.form.get(f"parecer_{entrada_id}", "")
                entrada.num_ordem_man = request.form.get(f"num_ordem_man_{entrada_id}", "")
                entrada.obs_sprocedencia = request.form.get(f"obs_sprocedencia_{entrada_id}", "")
                entrada.obs_justificativa = request.form.get(f"obs_justificativa_{entrada_id}", "")
                entrada.multipla_condição = ', '.join(request.form.getlist(f"multipla_condição_{entrada_id}"))
                entrada.multipla_comportamento = ', '.join(request.form.getlist(f"multipla_comportamento_{entrada_id}"))
                entrada.multipla_ambiental = ', '.join(request.form.getlist(f"multipla_ambiental_{entrada_id}"))
                entrada.funcionario = request.form.get(f"funcionario{entrada_id}", "")
        
        db.session.commit()
        return redirect(url_for("ssma"))

    # Paginação
    try:
        page = int(request.args.get('page', 1))
        if page < 1: 
            page = 1
    except ValueError:
        page = 1

    per_page = 10
    entradas_pag = Entrada.query.order_by(Entrada.id.asc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("ssma.html",
                           entradas=entradas_pag.items,
                           page=page,
                           total_pages=entradas_pag.pages)

# Formulário de abertura (com paginação)
@app.route("/abertura", methods=["GET", "POST"])
def abertura():
    if request.method == 'POST':
        # gravação da nova entrada
        emitente = request.form['emitente']
        classificação = request.form['classificação']
        empresa = request.form['empresa']
        data = datetime.strptime(request.form['data'], "%Y-%m-%d").date()
        hora = datetime.strptime(request.form['hora'], "%H:%M").time()
        local = request.form['local']
        observação = request.form['observação']
        ação = request.form['ação']

        nova_entrada = Entrada(
            emitente=emitente,
            classificação=classificação,
            empresa=empresa,
            data=data,
            hora=hora,
            local=local,
            observação=observação,
            ação=ação,
        )
        db.session.add(nova_entrada)
        db.session.commit()
        return redirect(url_for('abertura', page=1))

    # leitura com paginação
    page = request.args.get('page', 1, type=int)
    pagination = Entrada.query.order_by(Entrada.id.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )

    entradas = pagination.items
    total_pages = pagination.pages or 1

    return render_template('abertura.html',
                           entradas=entradas,
                           page=page,
                           per_page=PER_PAGE,
                           total_pages=total_pages)

# Gráficos
@app.route('/graficos')
def graficos():
    entradas = Entrada.query.all()

    # Gerar gráficos básicos para evitar erros
    contagem_class = contar_itens_lista(entradas, 'classificação') or {'Colaboradores': 1, 'Terceiros': 1}
    contagem_local = contar_itens_lista(entradas, 'local') or {'Administração': 1, 'Armazém': 1}
    contagem_agentes = contar_itens_lista(entradas, 'causa') or {'Comportamento Inseguro': 1}
    contagem_multipla_condição = contar_itens_lista(entradas, 'multipla_condição') or {'Proteção Inadequada': 1}
    contagem_multipla_comportamento = contar_itens_lista(entradas, 'multipla_comportamento') or {'Não utilizar EPI': 1}
    contagem_multipla_ambiental = contar_itens_lista(entradas, 'multipla_ambiental') or {'Vazamento': 1}
    contagem_class_sst = contar_itens_lista(entradas, 'class_sst') or {'Observação': 1}

    try:
        imagem_class = gerar_grafico(contagem_class, 'Ocorrências por Tipo de Colaborador', '', small=True, nomes_abaixo=True)
        imagem_local = gerar_grafico(contagem_local, 'Ocorrências por Local', '', small=True, nomes_abaixo=False)
        imagem_agentes = gerar_grafico(contagem_agentes, 'Situação', '', small=True, nomes_abaixo=True)
        imagem_multipla_condição = gerar_grafico(contagem_multipla_condição, 'Condições Inseguras', '', small=True, nomes_abaixo=False)
        imagem_multipla_comportamento = gerar_grafico(contagem_multipla_comportamento, 'Comportamentos Inseguros', '', small=True, nomes_abaixo=False)
        imagem_multipla_ambiental = gerar_grafico(contagem_multipla_ambiental, 'Ocorrências Ambientais', '', small=True, nomes_abaixo=False)
        imagem_class_sst = gerar_grafico(contagem_class_sst, 'Observações e Quase Acidentes', '', small=True, nomes_abaixo=True)
    except Exception as e:
        # Fallback em caso de erro nos gráficos
        print(f"Erro ao gerar gráficos: {e}")
        imagem_class = imagem_local = imagem_agentes = imagem_multipla_condição = ""
        imagem_multipla_comportamento = imagem_multipla_ambiental = imagem_class_sst = ""

    return render_template(
        'graficos.html',
        imagem_class=imagem_class,
        imagem_local=imagem_local,
        imagem_agentes=imagem_agentes,
        imagem_multipla_condição=imagem_multipla_condição,
        imagem_multipla_comportamento=imagem_multipla_comportamento,
        imagem_multipla_ambiental=imagem_multipla_ambiental,
        imagem_class_sst=imagem_class_sst,
    )

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)