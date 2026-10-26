"""
TripVault – Authentication blueprint
Routes: /login  /register  /logout
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from database.forms import LoginForm, RegistrationForm
from services.auth_service import create_user, verify_password, get_user_by_email
from services.email_service import send_welcome_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and verify_password(user, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = create_user(
            first_name = form.first_name.data,
            last_name  = form.last_name.data,
            email      = form.email.data,
            password   = form.password.data,
            phone      = form.phone.data or None,
        )
        login_user(user)
        send_welcome_email(user)
        flash(f'Account created! Welcome to TripVault, {user.first_name}!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
