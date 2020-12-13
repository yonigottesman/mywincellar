from flask import render_template, flash, redirect, url_for, request, abort, current_app ,send_from_directory
from flask_login import current_user, login_required
from app import db
from app.models import Wine
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.html")