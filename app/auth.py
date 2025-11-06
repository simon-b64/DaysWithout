import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

bp = Blueprint('auth', __name__)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


def anonymous_disabled(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if current_app.config['ANONYMOUS']:
            return redirect(url_for('index'))
        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
@anonymous_disabled
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = db.get_db()
        error = None

        user = database.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template("auth/login.html")


@bp.route('/register', methods=('GET', 'POST'))
@anonymous_disabled
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = db.get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif len(username) < 5 or len(username) > 40:
            error = 'Username must be between 5 and 40 characters.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 8 or len(password) > 20:
            error = 'Password must be between 8 and 20 characters.'

        if error is None:
            try:
                database.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                database.commit()
            except database.IntegrityError:
                error = 'User already exists.'
            else:
                flash('User was successfully created! You can now login!', 'success')
                return redirect(url_for('auth.login'))

        flash(error, 'error')

    return render_template("auth/register.html")


@bp.route('/logout')
@anonymous_disabled
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if current_app.config['ANONYMOUS']:
        g.user = {'id': 1, 'username': 'Anonymous'}
        return

    if user_id is None:
        g.user = None
    else:
        g.user = db.get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
