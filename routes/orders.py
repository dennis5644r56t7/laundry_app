from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Order, OrderItem, Service, MpesaTransaction
from services.mpesa import MpesaAPI

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': float(service.price)
    } for service in services])

@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    
    if not data or not data.get('services') or not data.get('pickup_address_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    order = Order(
        user_id=current_user.id,
        pickup_address_id=data['pickup_address_id'],
        delivery_address_id=data.get('delivery_address_id', data['pickup_address_id']),
        status='pending',
        notes=data.get('notes', '')
    )
    
    total_amount = 0
    for service_data in data['services']:
        service = Service.query.get(service_data['id'])
        if not service:
            return jsonify({'error': f'Service {service_data["id"]} not found'}), 404
        
        quantity = service_data.get('quantity', 1)
        total_amount += service.price * quantity
        order_item = OrderItem(
            order=order,
            service=service,
            quantity=quantity,
            price=service.price,
            subtotal=service.price * quantity
        )
        db.session.add(order_item)
    
    order.total_amount = total_amount
    db.session.add(order)
    db.session.commit()
    
    # Initiate M-Pesa payment if requested
    if data.get('pay_now'):
        try:
            mpesa = MpesaAPI()
            success, response = mpesa.initiate_stk_push(
                phone_number=current_user.phone_number,
                amount=total_amount,
                account_reference=str(order.id),
                description=f"Payment for order #{order.id}"
            )
            
            if not success:
                return jsonify({
                    'error': 'Payment initiation failed',
                    'details': response
                }), 400
            
            # Create M-Pesa transaction record
            transaction = MpesaTransaction(
                order_id=order.id,
                checkout_request_id=response['CheckoutRequestID'],
                merchant_request_id=response['MerchantRequestID'],
                amount=total_amount,
                status='pending'
            )
            db.session.add(transaction)
            db.session.commit()
            
            return jsonify({
                'message': 'Order created and payment initiated',
                'order_id': order.id,
                'payment_status': 'pending',
                'checkout_request_id': response['CheckoutRequestID']
            })
            
        except Exception as e:
            return jsonify({
                'error': 'Payment initiation failed',
                'details': str(e)
            }), 400
    
    return jsonify({
        'message': 'Order created successfully',
        'order_id': order.id
    })

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': order.id,
        'status': order.status,
        'total_amount': float(order.total_amount),
        'created_at': order.created_at.isoformat(),
        'services': [{
            'id': item.service.id,
            'name': item.service.name,
            'quantity': item.quantity,
            'price': float(item.service.price)
        } for item in order.order_items],
        'payment_status': order.payment_status
    })

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'status' in data:
        order.status = data['status']
        
    db.session.commit()
    
    return jsonify({
        'message': 'Order updated successfully',
        'order_id': order.id,
        'status': order.status
    })

@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_user_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Order.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
        
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'orders': [{
            'id': order.id,
            'status': order.status,
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.isoformat(),
            'payment_status': order.payment_status
        } for order in orders.items],
        'total': orders.total,
        'pages': orders.pages,
        'current_page': orders.page
    })
