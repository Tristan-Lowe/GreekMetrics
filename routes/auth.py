# routes/auth.py
from functools import wraps
from flask import (Blueprint, render_template, request, session,
                   redirect, url_for, flash, current_app)

auth_bp = Blueprint('auth', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def officer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') not in ('admin', 'officer'):
            return redirect(url_for('auth.login'))
        if session.get('role') == 'officer' and not session.get('officer_id'):
            return redirect(url_for('officer.select'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/')
def login():
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    if session.get('role') == 'officer' and session.get('officer_id'):
        return redirect(url_for('officer.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def do_login():
    password = request.form.get('password', '').strip()
    if password == current_app.config['ADMIN_PASSWORD']:
        session['role'] = 'admin'
        return redirect(url_for('admin.dashboard'))
    if password == current_app.config['OFFICER_PASSWORD']:
        session['role'] = 'officer'
        return redirect(url_for('officer.select'))
    flash('Invalid password.', 'error')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
