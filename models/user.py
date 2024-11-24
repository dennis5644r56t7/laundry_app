"""
This module defines the User model for the Kwamboka Laundry application.
The User model handles user information and authentication.
"""


from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        email (str): The user's email address.
        password_hash (str): The hashed password for authentication.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        phone_number (str): The user's phone number.
        is_active (bool): Indicates if the user's account is active.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def set_password(self, password):
        """
        Hashes the user's password.

        Args:
            password (str): The plaintext password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored password hash.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """
        Returns the user's full name by combining first and last names.

        Returns:
            str: The user's full name.
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """
        Provides a string representation of the user object.

        Returns:
            str: The string representation of the user.
        """
        return f'<User {self.email}>'
