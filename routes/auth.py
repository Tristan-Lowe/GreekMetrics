# routes/auth.py
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login():
    return 'login stub'
