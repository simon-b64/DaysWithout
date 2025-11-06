from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, g
)
from app.db import get_db
from datetime import datetime, date
from app.auth import login_required

bp = Blueprint('trackers', __name__)


# Helper function to calculate days between dates
def calculate_days(start_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    today = date.today()
    delta = today - start_date
    return delta.days


@bp.route('/')
@login_required
def index():
    database = get_db()
    trackers = database.execute(
        'SELECT id, name, start FROM days_without WHERE user_id = ? ORDER BY start DESC',
        (g.user['id'],)
    ).fetchall()

    # Convert to list of dicts with calculated days
    tracker_list = []
    for tracker in trackers:
        tracker_list.append({
            'id': tracker['id'],
            'name': tracker['name'],
            'start': tracker['start'],
            'days': calculate_days(tracker['start'])
        })

    return render_template('index.html', trackers=tracker_list)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        start = request.form.get('start')
        error = None

        if not name:
            error = 'Tracker name is required.'
        elif not start:
            error = 'Start date is required.'
        else:
            # Validate date is not in the future
            try:
                start_date = datetime.strptime(start, '%Y-%m-%d').date()
                if start_date > date.today():
                    error = 'Start date cannot be in the future.'
            except ValueError:
                error = 'Invalid date format.'

        if error is None:
            database = get_db()
            database.execute(
                'INSERT INTO days_without (name, start, user_id) VALUES (?, ?, ?)',
                (name, start, g.user['id'])
            )
            database.commit()
            flash('Tracker created successfully!', 'success')
            return redirect(url_for('index'))

        flash(error, 'error')

    return render_template('create.html', today=date.today().isoformat(), error=request.args.get('error'))


@bp.post('/reset/<int:id>')
@login_required
def reset(id):
    database = get_db()
    tracker = database.execute('SELECT * FROM days_without WHERE id = ? AND user_id = ?', (id, g.user['id'])).fetchone()

    if tracker is None:
        flash('Tracker not found.', 'error')
        return redirect(url_for('index'))

    database.execute('UPDATE days_without SET start = ? WHERE id = ?', (date.today().isoformat(), id))
    database.commit()
    flash(f'Tracker "{tracker["name"]}" has been reset!', 'success')
    return redirect(url_for('index'))


@bp.post('/delete/<int:id>')
@login_required
def delete(id):
    database = get_db()
    tracker = database.execute(
        'SELECT id, name, start FROM days_without WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()

    if tracker is None:
        flash('Tracker not found.', 'error')
        return redirect(url_for('index'))

    database.execute('DELETE FROM days_without WHERE id = ?', (id,))
    database.commit()
    flash(f'Tracker "{tracker["name"]}" has been deleted.', 'info')
    return redirect(url_for('index'))
