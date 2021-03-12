from flask import Blueprint

bp = Blueprint('wine', __name__)

from app.wine import routes
