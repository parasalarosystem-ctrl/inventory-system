from flask import Blueprint, jsonify
from app.models import Inventory

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([i.to_dict() for i in inventory])
