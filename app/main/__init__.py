from flask import Blueprint

main = Blueprint('main', __name__, template_folder='templates')

from . import routes  # import routes after blueprint is created
