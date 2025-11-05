import os
from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for, flash


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'days_without.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # Helper function to calculate days between dates
    def calculate_days(start_date):
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        today = date.today()
        delta = today - start_date
        return delta.days

    @app.route('/')
    def index():
        database = db.get_db()
        trackers = database.execute('SELECT id, name, start FROM days_without ORDER BY id DESC').fetchall()

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

    @app.route('/create', methods=('GET', 'POST'))
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
                database = db.get_db()
                database.execute('INSERT INTO days_without (name, start) VALUES (?, ?)', (name, start))
                database.commit()
                flash('Tracker created successfully!', 'success')
                return redirect(url_for('index'))

            flash(error, 'error')

        return render_template('create.html', today=date.today().isoformat(), error=request.args.get('error'))

    @app.post('/reset/<int:id>')
    def reset(id):
        database = db.get_db()
        tracker = database.execute('SELECT id, name, start FROM days_without WHERE id = ?', (id,)).fetchone()

        if tracker is None:
            flash('Tracker not found.', 'error')
            return redirect(url_for('index'))

        database.execute('UPDATE days_without SET start = ? WHERE id = ?', (date.today().isoformat(), id))
        database.commit()
        flash(f'Tracker "{tracker["name"]}" has been reset!', 'success')
        return redirect(url_for('index'))

    @app.post('/delete/<int:id>')
    def delete(id):
        database = db.get_db()
        tracker = database.execute('SELECT id, name, start FROM days_without WHERE id = ?', (id,)).fetchone()

        if tracker is None:
            flash('Tracker not found.', 'error')
            return redirect(url_for('index'))

        database.execute('DELETE FROM days_without WHERE id = ?', (id,))
        database.commit()
        flash(f'Tracker "{tracker["name"]}" has been deleted.', 'info')
        return redirect(url_for('index'))

    return app
