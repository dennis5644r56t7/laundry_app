from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Order, Payment, MpesaTransaction
from services.mpesa import MpesaAPI

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/mpesa/initiate', methods=['POST'])
@login_required
def initiate_mpesa_payment():
    data = request.get_json()
    order_id = data.get('order_id')
    phone_number = data.get('phone_number')
    
    if not order_id or not phone_number:
        return jsonify({'error': 'Missing required fields'}), 400
    
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method='mpesa',
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()
    
    # Initialize M-Pesa payment
    mpesa_api = MpesaAPI()
    response = mpesa_api.initiate_payment(
        phone_number=phone_number,
        amount=order.total_amount,
        reference=str(payment.id)
    )
    
    if response.get('success'):
        transaction = MpesaTransaction(
            payment_id=payment.id,
            transaction_id=response.get('transaction_id'),
            phone_number=phone_number,
            amount=order.total_amount,
            status='pending'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment initiated successfully',
            'transaction_id': transaction.transaction_id
        })
    
    return jsonify({'error': 'Failed to initiate payment'}), 400

@payments_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    
    transaction = MpesaTransaction.query.filter_by(transaction_id=transaction_id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Update transaction status
    transaction.status = data.get('status')
    transaction.result_code = data.get('result_code')
    transaction.result_description = data.get('result_description')
    
    # Update payment status
    if data.get('status') == 'completed':
        transaction.payment.status = 'completed'
        transaction.payment.order.status = 'paid'
    else:
        transaction.payment.status = 'failed'
    
    db.session.commit()
    return jsonify({'message': 'Callback processed successfully'})

@payments_bp.route('/mpesa/status/<transaction_id>', methods=['GET'])
@login_required
def check_payment_status(transaction_id):
    transaction = MpesaTransaction.query.filter_by(transaction_id=transaction_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
        
    order = Order.query.get(transaction.payment.order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    if transaction.status == 'pending':
        # Verify transaction status from M-Pesa
        try:
            mpesa = MpesaAPI()
            success, status = mpesa.query_stk_status(transaction.transaction_id)
            
            if not success:
                return jsonify({
                    'error': 'Status verification failed',
                    'details': status
                }), 400
                
            if status['ResultCode'] == 0:
                transaction.status = 'completed'
                transaction.transaction_code = status.get('TransactionCode', '')
                transaction.transaction_time = status.get('TransactionDate', '')
                transaction.payment.status = 'completed'
                transaction.payment.order.status = 'paid'
            elif status['ResultCode'] == 1:
                transaction.status = 'failed'
                transaction.result_description = status.get('ResultDesc', '')
                transaction.payment.status = 'failed'
            db.session.commit()
            
        except Exception as e:
            return jsonify({
                'error': 'Status verification failed',
                'details': str(e)
            }), 400
    
    return jsonify({
        'status': transaction.status,
        'transaction_code': transaction.transaction_code if transaction.status == 'completed' else None,
        'transaction_time': transaction.transaction_time if transaction.status == 'completed' else None,
        'result_description': transaction.result_description if transaction.status == 'failed' else None
    })
