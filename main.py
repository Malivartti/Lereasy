from flask import Flask, render_template
from data import db_session
from data.topics import Topic
from data.users import User
from werkzeug.utils import redirect
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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


@app.route("/login")
def login():
    return render_template("base.html")


@app.route("/topics")
def topics():
    db_session.global_init("db/topics.db")
    db_sess = db_session.create_session()
    it = db_sess.query(Topic).all()
    return render_template("topics.html", form=it)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=Flask)
