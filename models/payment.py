from datetime import datetime
from models import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # mpesa, card, etc.
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MpesaTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    mpesa_receipt_number = db.Column(db.String(50), unique=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # M-Pesa API specific fields
    checkout_request_id = db.Column(db.String(100))
    merchant_request_id = db.Column(db.String(100))
    result_code = db.Column(db.String(20))
    result_desc = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def customer_name(self):
        names = filter(None, [self.first_name, self.middle_name, self.last_name])
        return ' '.join(names)
