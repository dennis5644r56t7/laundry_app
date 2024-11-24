from datetime import datetime
from models import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Address references
    pickup_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    delivery_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)
    pickup_address = db.relationship('Address', foreign_keys=[pickup_address_id])
    delivery_address = db.relationship('Address', foreign_keys=[delivery_address_id])

    def calculate_total(self):
        return sum(item.subtotal for item in self.items)

    @property
    def payment_status(self):
        total_paid = sum(payment.amount for payment in self.payments if payment.status == 'completed')
        if total_paid >= self.total_amount:
            return 'paid'
        elif total_paid > 0:
            return 'partial'
        return 'unpaid'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    @property
    def subtotal(self):
        return self.quantity * self.price

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    estimated_time = db.Column(db.Integer)  # in hours
    is_active = db.Column(db.Boolean, default=True)
