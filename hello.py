# A very simple Flask Hello World app for you to get started with...
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask import request
from flask import make_response
from flask import redirect, url_for, flash, session
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = "Chave forte"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, index=True)
    descricao = db.Column(db.String(250), index=True)

class NameForm(FlaskForm):
    name = StringField("Qual é o nome do curso?", validators = [DataRequired()])
    descricao = TextAreaField('Descrição (250 caracteres)', validators = [DataRequired()])
    submit = SubmitField('Submit')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.route('/cursos', methods=['GET','POST'])
def cadastroCursos():
    form = NameForm()
    if form.validate_on_submit():
        curso = Curso.query.filter_by(nome=form.name.data).first()
        if curso is None:
            curso = Curso(nome=form.name.data, descricao=form.descricao.data)
            db.session.add(curso)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    cursos = Curso.query.order_by(Role.name).all()
    return render_template('cadastroCursos.html', form=form, nome=session.get('name'), known=session.get('known', False), cursos=cursos)

@app.route('/')
def index():
    return render_template('index.html', current_time = datetime.utcnow())

@app.route('/indisponivel')
def indisponivel():
    return render_template('indisponivel.html', current_time = datetime.utcnow())
