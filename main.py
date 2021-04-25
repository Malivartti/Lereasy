from flask import Flask, render_template, request
from data import db_session
from data.users import User
from data.topics import Topics
from flask_restful import abort
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.topic import TopicForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
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
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


#  <--------------------------------- Начальный экран --------------------------------->
@app.route("/")
def home():
    db_session.global_init("db/blogs.db")
    return render_template("home.html", title='Главная')


#  <--------------------------------- Профиль --------------------------------->
@app.route("/profile")
def profile():
    return render_template("profile.html", title='Профиль', form=current_user)


#  <--------------------------------- Вывод  Темы --------------------------------->
@app.route("/topics")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        topics = db_sess.query(Topics).filter(
            (Topics.user == current_user) | (Topics.is_private is not True))
    else:
        topics = db_sess.query(Topics).filter(Topics.is_private is not True)

    return render_template("topics.html", title='Темы', topics=topics)


#  <--------------------------------- Добавление  Темы --------------------------------->
@app.route('/topic', methods=['GET', 'POST'])
@login_required
def add_topic():
    form = TopicForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        topic = Topics()
        topic.title = form.title.data
        topic.content = form.content.data
        topic.is_private = form.is_private.data
        current_user.topics.append(topic)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/topics')
    return render_template('new_topic.html', title='Добавление темы', form=form)


#  <--------------------------------- Изменение Темы --------------------------------->
@app.route('/topic/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_topics(id):
    form = TopicForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        topics = db_sess.query(Topics).filter(Topics.id == id, Topics.user == current_user).first()
        if topics:
            form.title.data = topics.title
            form.content.data = topics.content
            form.is_private.data = topics.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        topics = db_sess.query(Topics).filter(Topics.id == id, Topics.user == current_user).first()
        if topics:
            topics.title = form.title.data
            topics.content = form.content.data
            print(request.form.get('photo'))  # ------------------------------------>
            # topics.img = request.form.get('photo')
            topics.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/topics')
        else:
            abort(404)
    return render_template('new_topic.html', title='Редактирование темы', form=form)


#  <--------------------------------- Удаление Темы --------------------------------->
@app.route('/topic_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def topics_delete(id):
    db_sess = db_session.create_session()
    topics = db_sess.query(Topics).filter(Topics.id == id, Topics.user == current_user).first()
    if topics:
        db_sess.delete(topics)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/topics')


@app.route('/certain/<int:id>')
def certain(id):
    db_sess = db_session.create_session()
    topic = db_sess.query(Topics).filter(Topics.id == id).first()
    if topic:
        return render_template('certain.html', title=topic.title, topic=topic, id=id)


@app.route('/practice/<int:id>')
def practice(id):
    db_sess = db_session.create_session()
    topics = db_sess.query(Topics).filter(Topics.id == id).first()
    if topics:
        return render_template('practice.html', title=topics.title, id=id)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
