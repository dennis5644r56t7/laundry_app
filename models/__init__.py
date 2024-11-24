from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to avoid circular imports
from .user import User
from .order import Order, OrderItem, Service
from .payment import Payment, MpesaTransaction
from .address import Address
