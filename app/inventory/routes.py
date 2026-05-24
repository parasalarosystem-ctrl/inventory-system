from flask import Blueprint, jsonify, redirect, url_for
from flask_login import current_user
from app.models import Inventory

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([i.to_dict() for i in inventory])
