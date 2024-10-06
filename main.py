from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, FLOAT, Date
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
import os
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap5(app)

class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///authenticate.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    contact_number: Mapped[int]= mapped_column(Integer, unique=True)
    
with app.app_context():
    db.create_all()
    
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)

