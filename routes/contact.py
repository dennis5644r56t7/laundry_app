from flask import Blueprint, flash, redirect, url_for, request

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    # Here you would typically send an email or save to database
    # For now, we'll just flash a success message
    flash('Thank you for your message! We will get back to you soon.', 'success')
    return redirect(url_for('index'))
