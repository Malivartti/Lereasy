from flask import Flask, render_template, request
from flask_login import login_required, LoginManager, login_user, logout_user
from werkzeug.security import check_password_hash

from data import db_session
from data.topics import Topic
from data.users import User
from werkzeug.utils import redirect
from forms.user import RegisterForm, AuthorizationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
manager = LoginManager(app)


# <------------------------------------------------------------>
@manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# <------------------------------------------------------------>

@app.route("/")
@app.route("/home")
def index():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    db_session.global_init("db/blogs.db")
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/home')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = AuthorizationForm()
    db_session.global_init("db/blogs.db")
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if check_password_hash(user.hashed_password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page)

        return render_template('login.html', title='Авторизация', form=form,
                               message="Неправильно введен логин или пароль")

    return render_template("login.html", title='Авторизация', form=form)


# <------------------------------------------------------------>
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return "Hello"


# <------------------------------------------------------------>

@app.route("/topics")
def topics():
    db_session.global_init("db/topics.db")
    db_sess = db_session.create_session()
    it = db_sess.query(Topic).all()
    return render_template("topics.html", form=it)


@app.route("/topics/<int:id>")
def particular_topic(id):
    return render_template("topic_block.html")


@app.route("/topics/id/material")
def material():
    return render_template("topic_block_material.html")


@app.route("/topics/id/practice")
def practice():
    return render_template("base.html")


# ----------------------- Видно администратору ----------------------
@app.route("/topics/<int:id>/ADmaterial", methods=['POST', 'GET'])
def ADmaterial(id):
    if request.method == 'GET':
        return render_template("topic_block_material.html")
    elif request.method == 'POST':
        print(request.form['name'])
        print(request.form['added_by'])
        print(request.form['img'])
        print(request.form['comment'])
        return 'True'


@app.route("/topics/<int:id>/ADpractice")
def ADpractice(id):
    return render_template("base.html")


@app.route("/topics/add")
def add_topic():
    pass


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=Flask)
