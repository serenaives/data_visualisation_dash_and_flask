from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from coursework_2.extensions import db
from coursework_2.forms import LoginForm, RegistrationForm, QuestionForm
from coursework_2.models import User, Questions

server_bp = Blueprint('main', __name__)


@server_bp.route('/')
def index():
    return render_template("index.html", title='Home Page')


@server_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Invalid username or password'
            return render_template('login.html', form=form, error=error)

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@server_bp.route('/logout/')
@login_required
def logout():
    logout_user()

    return redirect(url_for('main.index'))


@server_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)


@server_bp.route('/quiz_home/')
def quiz_home():
    return render_template("quiz_home.html", title='Quiz Home')


@server_bp.route('/quiz_play/<int:id>', methods=['GET', 'POST'])
@login_required
def quiz_play(id):
    form = QuestionForm()
    ques = Questions.query.filter_by(q_id=id).first()

    if not ques:
        return redirect(url_for('main.quiz_end'))

    if request.method == 'POST':
        option = request.form['options']
        return redirect(url_for('main.quiz_play', id=(id + 1)))

    form.options.choices = [(ques.option_a, ques.option_a), (ques.option_b, ques.option_b),
                            (ques.option_c, ques.option_c)]
    return render_template('quiz_play.html', form=form, q=ques, title='Quiz Play Question {}'.format(id))


@server_bp.route('/quiz_end/')
def quiz_end():
    return render_template("quiz_end.html", title='Quiz Home')


@server_bp.route('/leaderboard_home/')
def leaderboard_home():
    return render_template("leaderboard_home.html", title='Leaderboard Home')


@server_bp.route('/leaderboard_active/', methods=['GET', 'POST'])
@login_required
def leaderboard_active():
    if current_user.is_authenticated:
        return render_template("leaderboard_active.html", title='Leaderboard Active')
