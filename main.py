from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    send_from_directory,
    request,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, FLOAT, Date
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5
import datetime as dt
from chatBot import ChatBot
from table_generator import TableGenerator
import json

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
Bootstrap5(app)

table_path = None

chatbot = ChatBot()


class Base(DeclarativeBase):
    pass


# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///authenticate.db"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DB_URI", "sqlite:///authenticate.db"
)
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
    contact_number: Mapped[str] = mapped_column(String(15), unique=True)


with app.app_context():
    # db.drop_all()
    db.create_all()


class FormUser(FlaskForm):
    name = StringField(
        label="Name",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Regexp(
                r"^[A-Za-z]{2,}(?: [A-Za-z]+)*$",
                message="Please enter a valid name (no numbers or special characters, and at least 2 characters).",
            ),
        ],
    )
    email = EmailField(
        label="Email",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Email(message="Please enter a valid email address"),
        ],
    )
    password = PasswordField(
        label="Password",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Length(min=8, message="Your Password must contain at least 8 characters"),
        ],
    )
    contact_number = StringField(
        label="Contact",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Regexp(
                r"^\+?\d{10,15}$",
                message="Invalid phone number format. Include country code if needed.",
            ),
        ],
    )
    submit_button = SubmitField(label="Register")


class LoginUser(FlaskForm):
    email = EmailField(
        label="Email",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Email(message="Please enter a valid email address"),
        ],
    )
    password = PasswordField(
        label="Password",
        validators=[
            DataRequired(message="You can't leave this field empty"),
            Length(min=6, message="Your Password must contain at least 6 characters"),
        ],
    )
    submit_button = SubmitField(label="Login")


@app.route("/")
def home():
    return render_template("homepage.html", year=current_year)


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginUser()  # Renamed to avoid conflict
    if login_form.validate_on_submit():
        exiting_user = db.session.execute(
            db.select(User).where(User.email == login_form.email.data)
        ).scalar()
        if exiting_user:
            # Correct the check_password_hash function call
            if check_password_hash(exiting_user.password, login_form.password.data):
                login_user(exiting_user)  # Call the Flask-Login function
                return redirect(url_for("test_bot"))
            else:
                # flash("You've entered the wrong password, please try again!", 'error')
                return redirect(url_for("login"))
        else:
            # flash("That email doesn't exist, please try again or try registering!", 'info')
            return redirect(url_for("login"))
    return render_template(
        "login.html", logged_in=True, year=current_year, form=login_form
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    register_user = FormUser()
    if register_user.validate_on_submit():
        new_user = User(
            email=register_user.email.data,
            password=generate_password_hash(
                password=register_user.password.data,
                method="pbkdf2:sha256",
                salt_length=8,
            ),
            name=register_user.name.data,
            contact_number=register_user.contact_number.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("test_bot"))
    return render_template(
        "register.html", form=register_user, logged_in=True, year=current_year
    )


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/google_auth")
def google_auth():
    pass


@app.route("/github_auth")
def github_auth():
    pass


@app.route("/test_bot", methods=["GET", "POST"])
@login_required
def test_bot():
    global table_path
    if request.method == "POST":
        user_query = request.form.get("user_query")
        option = int(request.form.get("option"))
        prev_res = request.form.get("prev_res_id")

        # Safe-ish way to convert string dict to real dict
        if prev_res and prev_res.lower() not in ["none", "null"]:
            try:
                prev_res = json.loads(prev_res) if prev_res else None
            except json.JSONDecodeError:
                prev_res = None
        else:
            prev_res = None

        # Get ChatGPT response
        response, previous_res = chatbot.get_response(
            user_message=user_query, option=option, prev_response=prev_res
        )

        # If option 2 is selected, process with TableGenerator
        if option == 2:
            table_gen = TableGenerator(response)
            table_path = table_gen.generate_excel()
            table_df = table_gen.send_table()
            table_html = table_df.to_html(classes="table table-striped")
            return jsonify(
                {
                    "response": "",
                    "table_path": table_path,
                    "table_html": table_html,
                    "prev_res_id": {
                        "role": previous_res.role,
                        "content": previous_res.content,
                    },
                }
            )
        else:
            return jsonify(
                {
                    "response": response,
                    "prev_res_id": {
                        "role": previous_res.role,
                        "content": previous_res.content,
                    },
                }
            )

    return render_template("test_bot.html", logged_in=current_user.is_authenticated)


@app.route("/download/<path:filename>")
@login_required
def download(filename):
    return send_from_directory(os.path.join("testcases"), filename, as_attachment=True)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/reset-db")
def reset_db():
    try:
        db.drop_all()
        db.create_all()
        return "Database reset successful!", 200
    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(debug=False)
