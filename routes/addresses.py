from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Address

addresses_bp = Blueprint('addresses', __name__)

@addresses_bp.route('/', methods=['GET'])
@login_required
def list_addresses():
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': addr.id,
        'street': addr.street,
        'city': addr.city,
        'state': addr.state,
        'postal_code': addr.postal_code,
        'is_default': addr.is_default
    } for addr in addresses])

@addresses_bp.route('/', methods=['POST'])
@login_required
def create_address():
    data = request.get_json()
    
    address = Address(
        user_id=current_user.id,
        street=data.get('street'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=data.get('postal_code'),
        is_default=data.get('is_default', False)
    )
    
    if address.is_default:
        # Set all other addresses to non-default
        Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
    
    db.session.add(address)
    db.session.commit()
    
    return jsonify({
        'id': address.id,
        'street': address.street,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        'is_default': address.is_default
    }), 201

@addresses_bp.route('/<int:address_id>', methods=['PUT'])
@login_required
def update_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    address.street = data.get('street', address.street)
    address.city = data.get('city', address.city)
    address.state = data.get('state', address.state)
    address.postal_code = data.get('postal_code', address.postal_code)
    
    if data.get('is_default') and not address.is_default:
        # Set all other addresses to non-default
        Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        address.is_default = True
    
    db.session.commit()
    
    return jsonify({
        'id': address.id,
        'street': address.street,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        'is_default': address.is_default
    })

@addresses_bp.route('/<int:address_id>', methods=['DELETE'])
@login_required
def delete_address(address_id):
    address = Address.query.get_or_404(address_id)
    if address.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(address)
    db.session.commit()
    
    return '', 204
