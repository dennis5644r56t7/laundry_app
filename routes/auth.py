"""
This module defines the authentication routes for the Kwamboka Laundry application.
It includes routes for login, registration, and logout functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms.auth import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login requests.

    If the user is already authenticated, redirect them to the index page.
    Otherwise, validate the login form and authenticate the user if the form is valid.
    If the form is invalid, render the login page template with the form errors.

    Returns:
        Response: The login page template or redirect to the index page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration requests.

    If the user is already authenticated, redirect them to the index page.
    Otherwise, validate the registration form and create a new user if the form is valid.
    If the form is invalid, render the registration page template with the form errors.

    Returns:
        Response: The registration page template or redirect to the login page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user.

    Clear the user session and redirect to the index page with a logout message.

    Returns:
        Response: Redirect to the index page with a logout message.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handle forgot password requests.

    Returns:
        Response: The forgot password page template.
    """
    return render_template('forgot_password.html')
