from flask import Flask, redirect, render_template, request, url_for, session as s
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash
from database import session, Base, engine
from models import Livro, Usuario

Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.secret_key = 'chave'

@app.route("/")
def index():
    if 'user_id' not in s:
        usuario = None
    else:
        usuarios = session.scalars(select(Usuario)).all()
        livros = session.scalars(select(Livro)).all()
        user_id = s['user_id']
        usuario = session.scalars(select(Usuario).where(Usuario.id==user_id))
    return render_template('index.html', usuario=usuario)

@app.route("/usuario/novo", methods=["POST","GET"])
def new_user():
    if request.method == "POST":
        nome = request.form.get("nome", None)
        email = request.form.get("email", None)
        senha = request.form.get("senha", None)
        senha_hash = generate_password_hash(senha)

        if nome and email and senha:
            usuario = session.scalars(select(Usuario).where(Usuario.email==email)).first()

            if not usuario:
                usuario_novo = Usuario(nome=nome, email=email, senha=senha_hash)
                session.add(usuario_novo)
                session.commit()
                return redirect(url_for('login'))

            else:
                return redirect(url_for('new_user'))
            
    return render_template('cadastro.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        senha = request.form.get("senha", None)
        email = request.form.get("email", None)

        if senha and email:
            usuario = session.scalars(select(Usuario).where(Usuario.email==email)).first()

            if usuario and check_password_hash(usuario.senha, senha):
                s['user_id'] = usuario.id
                return redirect(url_for('listar_livro'))

            else:
                return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    s.pop('user_id', None)
    return redirect(url_for('index'))


@app.route("/livros/novo", methods=["POST","GET"])
def new_book():
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        user_id = request.form.get("usuario")

        if titulo and user_id:
            livro = session.scalars(select(Livro).where(Livro.titulo == titulo)).first()

            if not livro:
                livro_novo = Livro(titulo=titulo, usuario_id=int(user_id))
                session.add(livro_novo)
                session.commit()
                return redirect(url_for("listar_livro"))

    usuarios = session.scalars(select(Usuario).order_by(Usuario.nome)).all()
    return render_template("cadastro_livro.html", usuarios=usuarios)

@app.route("/livros/listar")
def listar_livro():
    livros = session.scalars(select(Livro).order_by(Livro.titulo)).all()
    return render_template("livros.html", livros=livros)


@app.route("/usuarios/listar")
def listar_usuarios():
    usuarios = session.scalars(select(Usuario).order_by(Usuario.nome)).all()
    return render_template("index.html", usuarios=usuarios)


