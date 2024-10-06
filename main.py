from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, FLOAT, Date
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5
import datetime as dt

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
current_year = dt.datetime.now().year

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
    
class FormUser(FlaskForm):
    name = StringField(label='Name', validators=[
        DataRequired(message="You can't leave this field empty"),
        Regexp(r'^[A-Za-z]{2,}(?: [A-Za-z]+)*$', message="Please enter a valid name (no numbers or special characters, and at least 2 characters).")
    ])
    email = EmailField(label='Email', validators=[DataRequired(message="You can't leave this field empty"),
                                                Email(message="Please enter a valid email address")])
    password = PasswordField(label='Password', validators=[DataRequired(message="You can't leave this field empty"), 
                                                            Length(min=8, message='Your Password must contain at least 8 characters')])
    contact_number = StringField(label='Contact',validators=[DataRequired(message="You can't leave this field empty"),
                                                    Regexp(r'^\d{10}$', message="Invalid phone number format. Please enter 10 digits.")])
    submit_button = SubmitField(label='Register')
    
class LoginUser(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired(message="You can't leave this field empty"),
                                                Email(message="Please enter a valid email address")])
    password = PasswordField(label='Password', validators=[DataRequired(message="You can't leave this field empty"), 
                                                            Length(min=6, message='Your Password must contain at least 6 characters')])
    submit_button = SubmitField(label='Login')
    

@app.route('/')
def home():
    return render_template('homepage.html', year = current_year)


@app.route('/login', methods = ['GET','POST'])
def login():
    login_user = LoginUser()
    if login_user.validate_on_submit():
        exiting_user = db.session.execute(db.select(User).where(User.email == login_user.email.data)).scalar()
        if exiting_user:
            if check_password_hash(password=login_user.password.data,pwhash=exiting_user.password): 
                login_user(exiting_user)
                # flash("User logged in successfully!", 'success')
                return redirect(url_for('test_bot'))
            else:
                # flash("You've entered wrong password, please try again!", 'error')
                return redirect(url_for('login'))
        else:
            # flash("That email doesn't exist, please try again or try registering!", 'info')
            return redirect(url_for('login'))
    return render_template('login.html', logged_in= True, year = current_year, form = login_user)

@app.route('/register', methods = ['GET', 'POST'])
def register():
    register_user = FormUser()
    if register_user.validate_on_submit():
        new_user = User(email = register_user.email.data,
                        password = generate_password_hash(password=register_user.password.data,
                                                        method='pbkdf2:sha256',
                                                        salt_length=8),
                        name = register_user.name.data,
                        contact_number = register_user.contact_number.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('test_bot'))
    return render_template('register.html', form=register_user, logged_in = True, year = current_year)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/test_bot')
@login_required
def test_bot():
    return render_template('test_bot.html',logged_in = current_user.is_authenticated)

@app.route('/google_auth')
def google_auth():
    pass

@app.route('/github_auth')
def github_auth():
    pass

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

